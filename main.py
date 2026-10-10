import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel,Field

load_dotenv()

class BookReview(BaseModel):
    title:str
    author:str
    rating_out_of_10: int=Field(
        ge=1, le=10,
        description=("A critical rating from 1 to 10 reflecting the general critical reception and reader consensus. "
            "1-3: Widely panned, poorly written, or universally low ratings. "
            "4-5: Below average or deeply flawed. "
            "6-7: Average/decent. "
            "8-10: Acclaimed classic or masterpiece. Do not inflate scores for notoriously poor books."
        ))
    key_takeaways:list[str]
    is_recommended:bool
    critical_flaws: list[str] = Field(
        description="Major criticisms, poor writing decisions, or reasons readers dislike the book."
    )

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt=input("Enter a book title to review: ")
response=client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_schema": BookReview,
    },
)

review: BookReview=BookReview.model_validate_json(response.text)

print(f"Title:{review.title}")
print(f"Score:{review.rating_out_of_10}/10")
print(f"Author:{review.author}")
print("Takeaways:")
print(f"Recommended:{review.is_recommended}")
for item in review.key_takeaways:
    print(f"-{item}")
print("Critical Flaws:")
for flaw in review.critical_flaws:
    print(f"-{flaw}")
