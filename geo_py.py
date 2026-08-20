import asyncio
from winrt.windows.devices.geolocation import (
    Geolocator,
    PositionAccuracy,
    GeolocationAccessStatus
)


async def get_location():
    # Ask Windows for permission
    access = await Geolocator.request_access_async()

    if access != GeolocationAccessStatus.ALLOWED:
        print("Location permission denied:", access)
        return

    # Create location provider
    locator = Geolocator()

    # Ask for high accuracy
    locator.desired_accuracy = PositionAccuracy.HIGH

    # Get current position
    position = await locator.get_geoposition_async()

    coordinate = position.coordinate

    print("Latitude :", coordinate.latitude)
    print("Longitude:", coordinate.longitude)
    print("Accuracy :", coordinate.accuracy, "meters")


asyncio.run(get_location())