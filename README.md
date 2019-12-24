# Tide Chart Calendar
A GitHub repo providing code to scrape data from US Harbors and convert into a visual tide chart superimposed on a calendar.

NOTE: Currently only works with Massachusetts towns, just need to update the output folders naming


Steps:
1) Visit the US Harbors website to choose a harbor location: https://www.usharbors.com
2) On US Harbors, navigate to the current monthly tide chart and extract the location specific details from the URL. For example, for Great Hill, MA, we extract 'massachusetts/great-hill-ma' from the URL https://www.usharbors.com/harbor/massachusetts/great-hill-ma/tides/#monthly-tide-chart
3) Paste the location from the URL into the "location" definition at the top of tide-chart-scrape.ipynb file
4) Change the desired year in tide-chart-scrape.ipynb
5) Run tide-chart-scrape.ipynb
6) Open create-calendars.Rmd and change the same two inputs: the year and the location
7) Run create-calendars.Rmd

Output: The output is in the form of 12 .pngs: one for each month of the year. It is located in the directory created automatically by the code which is identified by the requested year and location. 