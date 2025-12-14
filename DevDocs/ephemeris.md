# Ephemeris

To calculate the positions of the planets, the marsclock uses the approximations from E.M. Standish and J.G. Williams in their 1992 paper.
The values are reproduced here with details of how to use them:  

  - https://ssd.jpl.nasa.gov/planets/approx_pos.html

The JPL definitions do not include examples of to implement this in code and so it has been a process of trial and error. Code examples from the following resources were incredibly helpful for understanding how to implement the solution:

 - http://www.jgiesen.de/kepler/kepler.html
    - Includes a widget that calculates from the mean anomaly and eccentricity the eccentric and true anomaly as well as the source code to acheieve this.
 - https://www.johndcook.com/blog/2022/11/02/keplers-equation-python/
    - Code to solve keplers equation in python



The planet positions began with  the 'solar  widget' which shows relative positions of Earth and Mars.

The following resources have been really helpful for validating the outputs:
 - https://www.theplanetstoday.com/geocentric_orrery.html
 - https://theskylive.com/mars-info
 
 
The second phase was to show the position of the planets from Earth (geocentric), inspired by this webpage:
 - https://www.theplanetstoday.com/geocentric_orrery.html

Both widgets build on the code in this tutorial:
https://medium.com/analytics-vidhya/simulating-the-solar-system-with-under-100-lines-of-python-code-5c53b3039fc6

For the purposes of this project, it seems like overkill to plot planetary vectors. Instead, I pulled 300 years of planetary positions between 2000 and 2300 and calculated the average radians that each planet moves per day.
You can see in the notebook that there's a bit of error, especially for mercury, but it's accurate enough for the coarse level of detail shown on this display.
