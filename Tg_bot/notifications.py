import requests

from Tg_bot.handlers.handlers import get_user_info



async def get_progress_habit():
    user_data = await get_user_info()
    notification_data = []
    for tg_id, _ in user_data.items():
        response = requests.get(f'http://api:8000/api/notification/{tg_id}')
        if response.status_code == 200:
            data = response.json()
            notification_data.append({tg_id:data})
        else:
            continue
    return notification_data


