FROM opencvsharp_base
WORKDIR /app

COPY CameraServer.csproj CameraServer.csproj
RUN dotnet restore

COPY . .

RUN dotnet build

ENTRYPOINT [ "dotnet" "run" ]