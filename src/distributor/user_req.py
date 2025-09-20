from hashlib import md5


class UserReq:
    def __init__(
        self,
        user_id: str | int,
        payload: str | None,
        script_name: str,
        req_id: str | None = None
    ):
        self.user_id: str | int = user_id
        self.payload: str | None = str(payload).strip().lower() if payload is not None else None
        self.script_name: str = script_name
        
        if not req_id:
            hasher = md5()
            hasher.update(f"{self.payload}{self.script_name}".encode('utf8'))
            req_id = hasher.hexdigest()
        self.req_id: str = req_id
        

    def model_dump(self) -> dict:
        return {
            'user_id': self.user_id,
            'payload': self.payload,
            'script_name': self.script_name,
            'req_id': self.req_id
        }
    
    def __repr__(self):
        return str(self.model_dump())
