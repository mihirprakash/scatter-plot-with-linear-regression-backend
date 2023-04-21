import csv
from click import File
from fastapi import FastAPI, UploadFile
from typing import List
from pydantic import BaseModel
from scipy.stats import linregress

app = FastAPI()
data = set()

class DataPoint(BaseModel):
    x: float
    y: float
    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, DataPoint):
            return NotImplemented
        return self.x == other.x and self.y == other.y

class LinearRegressionResult(BaseModel):
    slope: float
    intercept: float
    r_squared: float


@app.post("/data/upload/")
async def upload_data(file: UploadFile = File(...)):
    contents = await file.read()
    lines = contents.decode('utf-8').split('\n')
    for line in lines[1:]:  # skip header row
        values = line.split(",")
        x = 0
        y = 0
        if len(values) != 2:
            x, y = 0, 0
        else:
            x, y = values
        dataPoint = DataPoint(x=float(x), y=float(y))
        data.add(dataPoint)
    print("length {0}".format(len(data)))
    return {"message": "Data uploaded successfully"}

@app.get("/data")
def get_data():
    global data
    return data

@app.get("/linear_regression")
def calculate_linear_regression():
    global data
    x = [point.x for point in data]
    y = [point.y for point in data]
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    r_squared = r_value ** 2
    return LinearRegressionResult(slope=slope, intercept=intercept, r_squared=r_squared)

