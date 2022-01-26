import math
import matplotlib.pyplot as plt
import requests
import numpy as np
import pandas as pd

API_KEY = "2f50f385d5789f4b2cfb1e5a2b11787b"

'''
A function to gather user parameters for lat/lon maximum and minimum values.
A try except while loop is used to repeatedly as for the correct format.
'''
def user_inputs():
    while True:
        try:
            latitude = input('min,max lat [Degrees] comma separated (eg 49.9,60.9): ')
            longitude = input('min,max long [Degrees] comma separated (eg −7.6,1.8): ')
            step = input('step increment (eg 1.2): ')
            latitude = latitude.split(',')
            longitude = longitude.split(',')
            float(step)
            [float(x) for x in latitude]
            [float(x) for x in longitude]
            break
        except ValueError:
            print("Incorrect format, please try again.")
    return latitude, longitude, step


'''
A function to calculate the lattice positions to query the API.
The queried data is then plotted on a contour quiver map to show wind speed and direction.
'''
def calculations(user_data):
    # user data: 0 = lat, 1 = long, 2 = step, 3 = out of bounds!
    lat = user_data[0]
    lon = user_data[1]
    step = user_data[2]
    # obtain spacing for lat/lon values for meshgrid
    latcounter = math.floor(abs(float(lat[1]) - float(lat[0])))
    longcounter = math.floor(abs(float(lon[1]) - float(lon[0])))
    latcounter = math.ceil(latcounter / float(step))
    longcounter = math.ceil(longcounter / float(step))
    # obtain the minimum and maximum values for meshgrid start and end
    xmin, xmax, ymin, ymax = float(lat[0]), float(lat[1]), float(lon[0]), float(lon[1])
    # linspace makes an array between two points with a set interval space
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, latcounter), np.linspace(ymin, ymax, longcounter))
    xcor = xx.flatten()
    ycor = yy.flatten()

    data_list = []
    print('Gathering data please wait. (Note, points retrieved may vary slightly).')
    # Gather all lattice datapoints
    for elem in range(len(xcor)):
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={xcor[elem]}&lon={ycor[elem]}&appid={API_KEY}'
        response = requests.get(url)
        data = response.json()
        data_list.append(data)

    # Retrieve only the windspeed and wind direction
    length = len(data_list)
    wind_speed = []
    wind_direction = []
    for elem in range(length):
        wind_speed.append(data_list[elem]['wind']['speed'])
        wind_direction.append(data_list[elem]['wind']['deg'])
    # a dataframe containing all relevant parameters
    df = pd.DataFrame(
        {'lat': xcor[:], 'lon': ycor[:], 'wind_speed': wind_speed[:], 'wind_direction': wind_direction[:]})
    print(df)
    # sin and cos the degree value to obtain UV for quiver plot
    df['wind_direction_cos'] = np.cos(df['wind_direction'][:])
    df['wind_direction_sin'] = np.sin(df['wind_direction'][:])
    # convert wind_speed and wind_direction into 2D arrays for contour/quiver plot
    pivot_speed = df.pivot(index='lat', columns='lon', values='wind_speed')
    pivot_direction_cos = df.pivot(index='lat', columns='lon', values='wind_direction_cos')
    pivot_direction_sin = df.pivot(index='lat', columns='lon', values='wind_direction_sin')

    fig, ax = plt.subplots(figsize=(6, 6))
    # plot the contour plot of wind speed intensity
    speed = ax.contourf(pivot_speed.columns, pivot_speed.index, pivot_speed.values)
    # plot the wind direction with arrows on top of the contour plot
    quiver = plt.quiver(pivot_direction_cos.columns, pivot_direction_cos.index, pivot_direction_cos,
                        pivot_direction_sin)
    fig.colorbar(speed, ax=ax)
    plt.title("A contour graph showing wind speeds and wind directions")
    plt.xlabel("longitude")
    plt.ylabel("latitude")
    plt.show()


if __name__ == '__main__':
    user_info = user_inputs()
    calculations(user_info)
