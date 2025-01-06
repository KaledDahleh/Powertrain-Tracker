import json
import boto3
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

def get_db_connection():
    # Get RDS credentials from AWS Secrets Manager
    secrets = boto3.client('secretsmanager')
    db_secret = secrets.get_secret_value(SecretId='r8-db-credentials')
    credentials = json.loads(db_secret['SecretString'])
    
    connection_string = f"postgresql://{credentials['username']}:{credentials['password']}@{credentials['host']}/{credentials['dbname']}"
    return create_engine(connection_string)

def predict_price(event, context):
    # Extract parameters
    params = event.get('queryStringParameters', {})
    transmission = params.get('transmission', 'manual')
    engine = params.get('engine', 'v10')
    
    # Connect to database
    engine = get_db_connection()
    
    # Get historical data
    query = """
    SELECT sale_price, sale_date, is_manual, is_v10, mileage
    FROM r8_sales
    WHERE is_manual = :is_manual AND is_v10 = :is_v10
    """
    
    df = pd.read_sql(query, engine, params={
        'is_manual': transmission == 'manual',
        'is_v10': engine == 'v10'
    })
    
    # Prepare data for prediction
    df['days_since_epoch'] = (df['sale_date'] - datetime(2008, 1, 1)).dt.days
    
    X = df[['days_since_epoch', 'mileage']]
    y = df['sale_price']
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)
    
    # Make prediction for next 6 months
    future_dates = pd.date_range(start=datetime.now(), periods=180, freq='D')
    future_days = [(date - datetime(2008, 1, 1)).days for date in future_dates]
    
    predictions = model.predict([[days, 10000] for days in future_days])  # Assume 10k miles
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'predictions': predictions.tolist(),
            'dates': [d.strftime('%Y-%m-%d') for d in future_dates],
            'accuracy': model.score(X_test, y_test)
        })
    }