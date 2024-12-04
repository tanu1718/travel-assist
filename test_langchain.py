import streamlit as st
from crewai import Agent, Task, Crew, Process
import requests

# Use Streamlit secrets for API keys
weather_api_key = st.secrets["OpenWeatherAPIkey"]
google_api_key = st.secrets["api_key"]
openai_api_key = st.secrets["key1"]

# Agent 1: Weather Fetcher
weather_agent = Agent(
    role="weather fetcher",
    goal="Fetch the weather information for a given location.",
    backstory="You are a weather expert, and your job is to fetch accurate weather information based on the location provided.",
    verbose=True,
    allow_delegation=False
)

# Agent 2: Places Finder
places_agent = Agent(
    role="places finder",
    goal="Search for places (restaurants, hotels, tourist spots) for a given location.",
    backstory="You are an expert in finding popular places based on the user's search criteria, using the Google Places API.",
    verbose=True,
    allow_delegation=False
)

# Agent 3: Recommendation Generator
recommendation_agent = Agent(
    role="recommendation generator",
    goal="Generate travel recommendations based on weather and places data.",
    backstory="You are a travel expert who generates personalized travel suggestions based on weather conditions and place details.",
    verbose=True,
    allow_delegation=False
)

# Task 1: Fetch weather data
weather_task = Task(
    description="Fetch weather data for a location.",
    agent=weather_agent,
    expected_output="Weather data in JSON format"
)

# Task 2: Fetch places based on the user's query
places_task = Task(
    description="Find places (restaurants, hotels, etc.) based on the user's search query.",
    agent=places_agent,
    expected_output="List of places in JSON format"
)

# Task 3: Generate recommendations based on weather and places
recommendation_task = Task(
    description="Generate personalized travel recommendations based on the weather and places data.",
    agent=recommendation_agent,
    expected_output="Travel recommendations in natural language"
)

# Create a Crew to manage the agents and tasks
crew = Crew(
    agents=[weather_agent, places_agent, recommendation_agent],
    tasks=[weather_task, places_task, recommendation_task],
    verbose=2,
    process=Process.sequential  # Sequential process: weather → places → recommendations
)

# Define functions to fetch weather and places
def get_weather_data(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}"
    response = requests.get(url)
    return response.json()

def fetch_places(query):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": google_api_key
    }
    response = requests.get(url, params=params)
    return response.json()

# Streamlit UI for user input
st.title("🌍 **Interactive Travel Guide Chatbot** 🤖")
st.markdown("Your personal travel assistant to explore amazing places.")

# User inputs for location and search
location = st.text_input("Enter the location for weather and places search (e.g., Paris, France):")
search_query = st.text_input("Enter what you're looking for (e.g., restaurants, hotels):")

if location and search_query:
    # Execute the Crew tasks
    output = crew.kickoff()

    # Process the output from the Crew execution
    weather_data = output[weather_task]  # Weather data from weather_agent
    places_data = output[places_task]    # Places data from places_agent

    # Weather data processing
    if weather_data:
        st.write(f"Weather for {location}: {weather_data['weather'][0]['description']}")

    # Places data processing
    if places_data:
        st.write(f"Top places in {location}:")
        for place in places_data['results'][:5]:
            st.write(f"{place['name']} - Rating: {place.get('rating', 'N/A')}")

    # Generate recommendations
    recommendations = output[recommendation_task]
    if recommendations:
        st.markdown("### 🌟 Travel Recommendations:")
        st.write(recommendations)
