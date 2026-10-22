def make_decision(temperature, humidity, soil_moisture):

    if soil_moisture < 30:
        return {
            "decision": "Sulama yap",
            "priority": "high",
            "reason": "Toprak nemi kritik seviyede dusuk"
        }

    elif soil_moisture < 45:
        return {
            "decision": "Toprak nemini takip et",
            "priority": "medium",
            "reason": "Toprak nemi orta seviyede"
        }

    else:
        return {
            "decision": "Sulama gerekli degil",
            "priority": "low",
            "reason": "Toprak nemi yeterli seviyede"
        }