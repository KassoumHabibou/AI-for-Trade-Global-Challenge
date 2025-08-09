## The AI for Trade Global Challenge — Full Details

As geopolitical and economic uncertainties reshape international commerce, accurate trade forecasts become crucial for businesses, policymakers, and researchers.

The AI for Trade Global Challenge invites data scientists, economists, and AI experts to explore the use of machine learning and statistics to improve trade forecasting.

### Goal
Teams will submit a forecast of the trade flows for the United States and China for the month of October of 2025. The forecast should provide trade values in dollars for the top 20 sources and destinations that trade at least 200 different products with the United States and China (at the HS4 product level). Teams must submit forecasts for exports and imports.

### Key Dates
Submissions are due on Oct 31, 2025 and will be evaluated as soon as fine-grained trade data for the US and China for the month of October becomes available (usually a couple of months after, e.g., during December).

### Eligibility
- Open to global participants (academics, industry professionals, students, and independent researchers)
- Teams of 1–5 members (individual submissions allowed)
- Multidisciplinary teams encouraged (AI/ML, economics, trade policy, data science)
- Each participant must belong to a single team
- All participants must be able to identify themselves as natural persons (no pseudonyms or “sock puppet” accounts)
- Teams must register to get access to the training data provided by the OEC
- Nobody who has worked directly at the OEC or CCL is eligible to participate

### Open Source
Teams are not required to open source their code, but are encouraged to do so. Before the final submission deadline, teams must submit a two-page description of their methods that would allow a person with reasonable technical skills to reproduce their forecast. Winning teams must present their results in an online event at the end of the challenge as a condition for claiming their prize.

### Resources
The Observatory of Economic Complexity will make available trade data for the United States and China for all months of the years 2023 and 2024. Teams can use this data, and any additional data, to create and test their models.

### Allowed Methods
Any forecasting method is allowed—general equilibrium models, regressions, neural networks, ensembles, hybrids—so long as the output adheres to the submission format.

### Submission Guidelines
Teams must submit a plain text “.csv” file with their predictions by midnight Oct 31, 2025 (Central European Time). The file must adhere to the following format:

Columns: "Country1","Country2","ProductCode","TradeFlow","Value"

- Countries: ISO 3-letter codes
- Products: 4 digit HS codes (HS4)
- TradeFlow: `Export` or `Import`
- Value: USD

Example rows:

"USA","CHL","8404","Export","1234567"

"USA","CHN","8405","Import","1234567"

Method descriptions should be two pages—direct, technically detailed, and sufficient for a practitioner to reproduce the forecast.

### Evaluation
Trade flow predictions for the US and China will be evaluated against data published respectively by these countries (US forecasts will be compared with US data and China forecasts with Chinese data). The winning team will be the one with the best forecast according to sMAPE (symmetric mean absolute percentage error).

To be eligible for the prize, all forecasts must pass a minimum requirement of having a higher accuracy than a forecast based on simply using the latest raw trade data available at the time of submission (likely July or August 2025). For example, the forecast for October trade numbers must be better than simply using trade data for July (assuming that data is available).

### Prizes
- First Prize: 3000 USD + free OEC Premium accounts for 1 year for all team members
- Second Prize: 2000 USD + free OEC Premium accounts for 1 year for all team members
- Third Prize: 1000 USD + free OEC Premium accounts for 1 year for all team members

### Partners
The AI for Trade Global Challenge is organized by the Center for Collective Learning in partnership with:

- The Observatory of Economic Complexity (Strategic Data Partner) 
- Trade Practice, The World Bank
- Asian Development Bank 
- European Lighthouse of AI for Sustainability (ELIAS)
- The Supply Chain AI Lab at the University of Cambridge
- Complexity Economics Group, INET Oxford University
- MIOIR, AMBS, University of Manchester
- Corvinus Institute of Advanced Studies (CIAS), Corvinus University of Budapest 
- Institute for Advanced Study in Toulouse (IAST), Toulouse School of Economics
- Fundación Cotec, Spain 
- Global Opportunity Lab at UC Berkeley

### Why not Kaggle?
Kaggle does not support future out-of-sample challenges (it requires an immediate solution file). The future out-of-sample design here improves fairness and rigor; therefore, the challenge is hosted independently.

