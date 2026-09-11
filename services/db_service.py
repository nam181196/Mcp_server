import os
import sys
import json
from datetime import datetime

# Đảm bảo thư mục gốc dự án nằm trong sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pyrefly: ignore [missing-import]
import pymongo
# pyrefly: ignore [missing-import]
from bson import ObjectId
from config.db_config import MONGODB_URI, MONGODB_DB_NAME

def serialize_mongo_item(item):
    """Chuyển đổi dữ liệu MongoDB (ObjectId, datetime) thành định dạng JSON hợp lệ."""
    if item is None:
        return None
    if isinstance(item, list):
        return [serialize_mongo_item(i) for i in item]
    if isinstance(item, dict):
        result = {}
        for k, v in item.items():
            if k == "_id":
                result["_id"] = str(v)
                result["id"] = str(v)
            elif isinstance(v, ObjectId):
                result[k] = str(v)
            elif isinstance(v, datetime):
                result[k] = v.isoformat()
            elif isinstance(v, (dict, list)):
                result[k] = serialize_mongo_item(v)
            else:
                result[k] = v
        return result
    return item

class DBService:
    """Service thao tác trực tiếp với Database MongoDB."""

    def __init__(self, uri: str = None, db_name: str = None):
        self.uri = uri or MONGODB_URI
        self.db_name = db_name or MONGODB_DB_NAME
        self._client = None
        self._db = None

    def get_db(self):
        """Khởi tạo hoặc trả về instance kết nối tới MongoDB database."""
        if self._db is None:
            self._client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self._db = self._client[self.db_name]
        return self._db

    def is_connected(self) -> bool:
        """Kiểm tra xem máy chủ MongoDB có đang hoạt động hay không."""
        try:
            client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            return True
        except Exception:
            return False

    # -------------------------------------------------------------
    # 1. TRUY VẤN MONGODB TRỰC TIẾP DÀNH CHO DB TOOLS
    # -------------------------------------------------------------

    def get_collection_stats(self) -> dict:
        """Lấy danh sách các Collection và thống kê số lượng bản ghi."""
        db = self.get_db()
        collections = db.list_collection_names()
        stats = {}
        for name in collections:
            count = db[name].count_documents({})
            stats[name] = count
        return {"database": self.db_name, "collections": stats}

    def find_documents(self, collection_name: str, filter_dict: dict = None, limit: int = 50) -> list:
        """Tìm kiếm document trong collection."""
        db = self.get_db()
        query = filter_dict or {}
        
        # Nếu truyền _id là chuỗi hex 24 ký tự, tự động parse sang ObjectId
        if "_id" in query and isinstance(query["_id"], str) and len(query["_id"]) == 24:
            try:
                query["_id"] = ObjectId(query["_id"])
            except Exception:
                pass

        cursor = db[collection_name].find(query).limit(limit)
        docs = list(cursor)
        return serialize_mongo_item(docs)

    def insert_document(self, collection_name: str, document_dict: dict) -> dict:
        """Thêm document mới vào collection."""
        db = self.get_db()
        if "created_at" not in document_dict:
            document_dict["created_at"] = datetime.utcnow().isoformat()
        result = db[collection_name].insert_one(document_dict)
        document_dict["_id"] = str(result.inserted_id)
        document_dict["id"] = str(result.inserted_id)
        return serialize_mongo_item(document_dict)

    def update_document(self, collection_name: str, filter_dict: dict, update_dict: dict) -> dict:
        """Cập nhật document trong collection."""
        db = self.get_db()
        query = filter_dict or {}
        if "_id" in query and isinstance(query["_id"], str) and len(query["_id"]) == 24:
            try:
                query["_id"] = ObjectId(query["_id"])
            except Exception:
                pass

        # Đảm bảo cấu trúc $set nếu không có toán tử mongodb
        if not any(k.startswith("$") for k in update_dict.keys()):
            update_payload = {"$set": update_dict}
        else:
            update_payload = update_dict

        res = db[collection_name].update_many(query, update_payload)
        return {
            "matched_count": res.matched_count,
            "modified_count": res.modified_count,
            "acknowledged": res.acknowledged
        }

    def delete_document(self, collection_name: str, filter_dict: dict) -> dict:
        """Xoá document khỏi collection."""
        db = self.get_db()
        query = filter_dict or {}
        if "_id" in query and isinstance(query["_id"], str) and len(query["_id"]) == 24:
            try:
                query["_id"] = ObjectId(query["_id"])
            except Exception:
                pass

        res = db[collection_name].delete_many(query)
        return {
            "deleted_count": res.deleted_count,
            "acknowledged": res.acknowledged
        }

    # -------------------------------------------------------------
    # 2. XỬ LÝ FALLBACK CHO WEBSHOP CLIENT KHI BACKEND SẬP
    # -------------------------------------------------------------

    def handle_fallback_request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> str:
        """Xử lý yêu cầu HTTP endpoint dưới dạng truy vấn MongoDB trực tiếp."""
        endpoint_clean = endpoint.strip("/").lower()
        method_upper = method.upper()
        db = self.get_db()

        try:
            # GET /products
            if method_upper == "GET" and endpoint_clean == "products":
                query = {}
                if params and "category" in params:
                    query["category"] = params["category"]
                docs = list(db["products"].find(query))
                return json.dumps(serialize_mongo_item(docs), indent=2, ensure_ascii=False)

            # GET /products/{id}
            elif method_upper == "GET" and endpoint_clean.startswith("products/"):
                prod_id = endpoint_clean.split("products/")[1]
                query = {"$or": [{"_id": ObjectId(prod_id) if len(prod_id) == 24 else prod_id}, {"id": prod_id}]}
                doc = db["products"].find_one(query)
                if doc:
                    return json.dumps(serialize_mongo_item(doc), indent=2, ensure_ascii=False)
                return json.dumps({"error": f"Không tìm thấy sản phẩm với ID: {prod_id}"}, ensure_ascii=False)

            # POST /products (Admin create product)
            elif method_upper == "POST" and endpoint_clean == "products":
                payload = data or {}
                if "created_at" not in payload:
                    payload["created_at"] = datetime.utcnow().isoformat()
                res = db["products"].insert_one(payload)
                payload["_id"] = str(res.inserted_id)
                payload["id"] = str(res.inserted_id)
                return json.dumps(serialize_mongo_item(payload), indent=2, ensure_ascii=False)

            # PUT /products/{id} (Admin update product)
            elif method_upper == "PUT" and endpoint_clean.startswith("products/"):
                prod_id = endpoint_clean.split("products/")[1]
                query = {"$or": [{"_id": ObjectId(prod_id) if len(prod_id) == 24 else prod_id}, {"id": prod_id}]}
                payload = data or {}
                res = db["products"].update_one(query, {"$set": payload})
                return json.dumps({
                    "message": "Cập nhật sản phẩm thành công qua DB direct",
                    "matched_count": res.matched_count,
                    "modified_count": res.modified_count
                }, ensure_ascii=False)

            # DELETE /products/{id} (Admin delete product)
            elif method_upper == "DELETE" and endpoint_clean.startswith("products/"):
                prod_id = endpoint_clean.split("products/")[1]
                query = {"$or": [{"_id": ObjectId(prod_id) if len(prod_id) == 24 else prod_id}, {"id": prod_id}]}
                res = db["products"].delete_one(query)
                return json.dumps({
                    "message": "Xoá sản phẩm thành công qua DB direct",
                    "deleted_count": res.deleted_count
                }, ensure_ascii=False)

            # GET /my-orders hoặc GET /orders
            elif method_upper == "GET" and (endpoint_clean in ("my-orders", "orders")):
                docs = list(db["orders"].find({}))
                return json.dumps(serialize_mongo_item(docs), indent=2, ensure_ascii=False)

            # GET /orders/stats
            elif method_upper == "GET" and endpoint_clean == "orders/stats":
                total_orders = db["orders"].count_documents({})
                pipeline = [{"$group": {"_id": None, "total_revenue": {"$sum": "$total_price"}}}]
                agg = list(db["orders"].aggregate(pipeline))
                total_revenue = agg[0]["total_revenue"] if agg else 0
                return json.dumps({
                    "total_orders": total_orders,
                    "total_revenue": total_revenue,
                    "source": "MongoDB Direct"
                }, indent=2, ensure_ascii=False)

            # GET /orders/{id}
            elif method_upper == "GET" and endpoint_clean.startswith("orders/"):
                order_id = endpoint_clean.split("orders/")[1]
                query = {"$or": [{"_id": ObjectId(order_id) if len(order_id) == 24 else order_id}, {"id": order_id}]}
                doc = db["orders"].find_one(query)
                if doc:
                    return json.dumps(serialize_mongo_item(doc), indent=2, ensure_ascii=False)
                return json.dumps({"error": f"Không tìm thấy đơn hàng với ID: {order_id}"}, ensure_ascii=False)

            # POST /orders (Create order)
            elif method_upper == "POST" and endpoint_clean == "orders":
                payload = data or {}
                if "created_at" not in payload:
                    payload["created_at"] = datetime.utcnow().isoformat()
                res = db["orders"].insert_one(payload)
                payload["_id"] = str(res.inserted_id)
                payload["id"] = str(res.inserted_id)
                return json.dumps(serialize_mongo_item(payload), indent=2, ensure_ascii=False)

            # GET /users (Admin get all users)
            elif method_upper == "GET" and endpoint_clean == "users":
                docs = list(db["users"].find({}))
                return json.dumps(serialize_mongo_item(docs), indent=2, ensure_ascii=False)

            # Generic fallback cho các collection khác
            else:
                col_name = endpoint_clean.split("/")[0]
                if col_name in db.list_collection_names():
                    docs = list(db[col_name].find({}).limit(50))
                    return json.dumps(serialize_mongo_item(docs), indent=2, ensure_ascii=False)

                return json.dumps({
                    "warning": f"Endpoint '{endpoint}' được xử lý ở chế độ Fallback DB mặc định (chưa có handler riêng).",
                    "status": "fallback_exec_ok"
                }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "error": f"Lỗi truy vấn trực tiếp MongoDB Fallback: {str(e)}"
            }, ensure_ascii=False)

db_service = DBService()
