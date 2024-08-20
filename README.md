# Robdantic
A Pydantic dataclass BaseModel for decoding/encoding Geometry Dash Robtop Strings. 
This is part of a planned replacement library for gdpy whith better functionality 
along with a greater lifespan although everything is currently in it's concept phase
and may require a few more things but for the most part you can copy and paste the code until 
I can get around to uploading this to pypi.

## Examples
```python
# Note: Field is different from a Pydantic field
from robdantic import RobtopModel, Field

class SimpleModel(RobtopModel):
    x: int = Field(key=1)
    y: int = Field(key=2)

model = SimpleModel.from_robtop(b"1~10~2~699", splitter=b"~")
print((model.x, model.y))
```


```python
# Robdantic can also take splitter parameters as a subclass argument.
class NameModel(RobtopModel, split=b":"):
    name:str = Field(key=1)

model = Model2.from_robtop(b"1:john doe")
assert model.name == "john doe"
# re-encode the model to bytes format
print(model.to_robtop())
```

