Set up data:

Dashboard url for analysis: https://app.amplitude.com/analytics/thortful/dashboard/6pqbsp18

Chart Name: Sessions (Current Year)
Chart ID: y0ivh3am

Chart Name: Sessions (Previous Year)
Chart ID: 5vbaz782

Chart Name: Sessions per user (Current Year)
Chart ID: pc9c0crz

Chart Name: Sessions per user (Previous Year)
Chart ID: 3d400y6n

Chart Name: Session Conversion % (Current Year)
Chart ID: 42c5gcv4

Chart Name: Session Conversion % (Previous Year)
Chart ID: 3t0wgn4i

Chart Name: User Conversion %
Chart ID: 4j2gp4ph



API Information:
- Session charts cannot be queried using the built in comparison function, which generates a row of data for the previous year, using the prefix of [Previous], therefore the approach is to combine 2 different charts (Current Year) and (Previous Year) to get a YoY result.

- Other charts such as segmentation or funnel charts can use this, so do not need to combine multiple charts together to achieve the end goal.

Desired output format:

An example of an executive summary is this:

Conversion trends as outlined above: sessions down 11% YOY, but session conversion 2 ppts better YOY. Web session conversion was up 3 ppts YOY & user conversion up 5ppt YoY (to be expected with lower sessions), while App was down by -1ppt on session CVR and -1ppt on user CVR.

Key things we're looking for:

- Call out the iSO Week within the year For the previous week, starting Monday, ending Sunday labelled e.g. 'Week 29'
- Call out the dates that are being analysed
- Call out each result being analysed for each platform (Apps, Web & App + Web Combined)
- The results should be rounded to 1 decimal place.
- We want to know the result for the target week and then to show the difference against the result last week. 
- We want to know how that Year on Year result compares to last weeks Year on Year result. e.g. has this week improved or declined against last weeks Year on Year result.