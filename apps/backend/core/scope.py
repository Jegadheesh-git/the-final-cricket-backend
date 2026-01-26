class Scope:

    def __init__(self, owner_type, owner_id, role, subscription, allow_system_data):
        self.owner_type = owner_type
        self.owner_id = owner_id
        self.role = role
        self.subscription = subscription
        self.allow_system_data = allow_system_data

    def is_org(self):
        return self.owner_type == "ORG"

    def is_user(self):
        return self.owner_type == "USER"