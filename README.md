# Robdantic
A Pydantic dataclass BaseModel for decoding/encoding Geometry Dash Robtop Strings. 
This is part of a planned replacement library for gdpy whith better functionality 
along with a greater lifespan although everything is currently in it's concept phase
and may require a few more things such as `__init_subclass__` values for delimiters
which has yet to come. I already figured out how to do it I just haven't written it yet.


## Example
```python
# Note: Field is different from a Pydantic field
from robdantic import RobtopModel, Field
class SimpleModel(RobtopModel):
    x: int = Field(key=1)
    y: int = Field(key=2)

model = SimpleModel.from_robtop(b"1~10~2~699", splitter=b"~")
print((model.x, model.y))
```



