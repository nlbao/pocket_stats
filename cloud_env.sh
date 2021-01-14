printenv > .env

echo "POCKET_STATS_CONSUMER_KEY = $POCKET_STATS_CONSUMER_KEY"

sed -i 's/%POCKET_STATS_CONSUMER_KEY%/'$POCKET_STATS_CONSUMER_KEY'/g' app.yaml
sed -i 's/%GTAG_ID%/'$GTAG_ID'/g' app.yaml

cat app.yaml
