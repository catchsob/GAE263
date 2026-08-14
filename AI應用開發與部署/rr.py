from google import genai
from google.genai.types import Part, Content
from google.oauth2 import service_account


print(f'my name is: {__name__}')


def recognize_plates(image: bytes, mime_type='image/jpeg', model='gemini-3.5-flash', service='service.json') -> list[str]:
    # initialization
    credentials = service_account.Credentials.from_service_account_file(
        'service.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    genai_client = genai.Client(
        enterprise=True,
        location='global',
        project=credentials.project_id,
        credentials=credentials
    )
    
    response_schema = {
        "type": "object",
        "properties": {
            "plates": {
                "type": "array",
                "description": "儲存多個車牌號碼，若找不到車牌則為空 array", 
                "items": {
                    "type": "string",
                    "description": "車牌號碼"
                }
            },
            "cars": {
                "type": "integer",
                "description": "照片中的汽車數量", 
            }
        },
        "required": ["plates", "cars"]
    }
    
    config = {
        'max_output_tokens': 100,
        'response_mime_type': 'application/json',
        'response_schema': response_schema,
        'thinking_config': {'thinking_budget': 0}
    }
    
    data = Part.from_bytes(data=image, mime_type=mime_type)
    
    contents = [Content(role='user', parts=[data])]
    
    response = genai_client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )

    return response.parsed.get('plates', [])
