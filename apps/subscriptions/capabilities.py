PLAN_CAPABILITIES = {
    
    "SOLO_FREE": {
        "limits": {"devices":1,"stadiums":3},
        "features": {"offline":False}
    },

    "SOLO_PRO_MONTHLY": {
        "limits": {"devices":1,"stadiums":4},
        "features": {"offline": True}
    },

    "ORG_BASIC_MONTHLY": {
        "limits": {"devices":2,"users":3,"stadiums":5},
        "features": {"invite_users":True}
    },

    "ORG_ENTERPRISE_YEARLY": {
        "limits": {"devices":3,"users":3, "stadiums": None},
        "features": {"invite_users": True, "priority_support":True}
    }

}