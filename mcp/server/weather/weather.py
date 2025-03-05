from typing import Any
import httpx
import logging
import sys
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("weather_server")

logger.info("Starting weather server initialization")
try:
    # Initialize FastMCP server
    logger.debug("Creating FastMCP instance")
    mcp = FastMCP("weather")
    logger.info("FastMCP server initialized successfully")
except Exception as e:
    logger.error(f"Error initializing FastMCP: {str(e)}", exc_info=True)
    raise

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    logger.debug(f"Making NWS API request to: {url}")
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            logger.debug(f"Sending GET request with headers: {headers}")
            response = await client.get(url, headers=headers, timeout=30.0)
            logger.debug(f"Received response with status code: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            logger.debug("Successfully parsed JSON response")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during API request: {e.response.status_code} - {str(e)}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error during API request: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}", exc_info=True)
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    logger.info(f"Getting alerts for state: {state}")
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    logger.debug(f"Constructed URL: {url}")
    
    data = await make_nws_request(url)
    logger.debug(f"Received data from make_nws_request: {data is not None}")

    if not data or "features" not in data:
        logger.warning(f"No valid data returned for state {state}")
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        logger.info(f"No active alerts for state {state}")
        return "No active alerts for this state."

    logger.debug(f"Found {len(data['features'])} alerts for state {state}")
    alerts = [format_alert(feature) for feature in data["features"]]
    result = "\n---\n".join(alerts)
    logger.debug("Successfully formatted alerts")
    return result

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    logger.info(f"Getting forecast for coordinates: {latitude}, {longitude}")
    
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    logger.debug(f"Constructed points URL: {points_url}")
    
    points_data = await make_nws_request(points_url)
    logger.debug(f"Received points data: {points_data is not None}")

    if not points_data:
        logger.warning(f"Failed to get points data for coordinates: {latitude}, {longitude}")
        return "Unable to fetch forecast data for this location."

    try:
        # Get the forecast URL from the points response
        forecast_url = points_data["properties"]["forecast"]
        logger.debug(f"Extracted forecast URL: {forecast_url}")
        
        forecast_data = await make_nws_request(forecast_url)
        logger.debug(f"Received forecast data: {forecast_data is not None}")

        if not forecast_data:
            logger.warning(f"Failed to get forecast data from URL: {forecast_url}")
            return "Unable to fetch detailed forecast."

        # Format the periods into a readable forecast
        periods = forecast_data["properties"]["periods"]
        logger.debug(f"Found {len(periods)} forecast periods")
        
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            logger.debug(f"Processing period: {period['name']}")
            forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
            forecasts.append(forecast)

        result = "\n---\n".join(forecasts)
        logger.debug("Successfully formatted forecast")
        return result
    except KeyError as e:
        logger.error(f"KeyError while processing forecast data: {str(e)}", exc_info=True)
        return f"Error processing forecast data: missing key {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error while processing forecast: {str(e)}", exc_info=True)
        return f"Error processing forecast: {str(e)}"


if __name__ == "__main__":
    # Initialize and run the server
    logger.info("Starting MCP server with stdio transport")
    try:
        logger.debug("Calling mcp.run()")
        mcp.run(transport='stdio')
        logger.info("MCP server completed successfully")
    except Exception as e:
        logger.error(f"Error running MCP server: {str(e)}", exc_info=True)
        raise
