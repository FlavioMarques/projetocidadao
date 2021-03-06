import altair as alt
import datapane as dp
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')
countries = df['location'].sample(3)

subset = df[df.location.isin(countries)]

base = alt.Chart(subset).encode(
    x='date:T',
    color='location'
).mark_line(
    size=5,
    opacity=0.75,
).interactive()

plots = [
  base.encode(y='total_vaccinations_per_hundred'),
  base.encode(y='daily_vaccinations_per_million'),
  base.encode(y='people_vaccinated')
]

report = dp.Report(
    dp.Text(f"## Covid vaccinations in {', '.join(countries)}"),
    dp.Group(*plots[:2], columns=2),
    plots[2],
    dp.DataTable(subset, caption=f'Dataset for {countries}'),
)

report.publish(name='My Covid Report', open=True)