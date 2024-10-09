# Gradient Sentry-Node
An unofficial Docker Image for [gradient.network](https://app.gradient.network/signup?code=STFUMU)
Available on [Docker Hub](https://hub.docker.com/r/sicnull/gradient-sentry-node)


## How to get started?
1. Register a Gradient Account if you don't have one already: [gradient.network](https://app.gradient.network/signup?code=STFUMU)
2. Either build this image from source, or download it from Docker Hub
3. Set envriomental variables to their respective values: GRADIENT_USER and GRADIENT_PASS
4. You're good to go!

### Docker Run Command
```
docker run -d \
    --name gradient \
    --restart always \
    -e GRADIENT_USER=myuser@mail.com \
    -e GRADIENT_PASS=mypass \
    -e ALLOW_DEBUG=False \
    -v gradient_data:/app/data \
    sicnull/gradient-sentry-node
```
## License
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

