from pydantic import BaseModel, Field

class PatientData(BaseModel):
    age: float = Field(...)
    sex: float = Field(...)
    bmi: float = Field(...)
    bp: float = Field(...)
    s1: float = Field(...)
    s2: float = Field(...)
    s3: float = Field(...)
    s4: float = Field(...)
    s5: float = Field(...)
    s6: float = Field(...)

class PredictionResponse(BaseModel):
    predict: float
