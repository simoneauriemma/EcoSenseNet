import { APIGatewayProxyEvent } from "aws-lambda"
import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb"

const REGION = process.env.REGION

//db client
const ddbClient = new DynamoDBClient({ region: REGION, endpoint: "http://localhost:4566" })

//get timestamp
let new_Date = Date.now().toString()
let fullDate = new Date().toLocaleString()

const POLLUTION_QUEUE_NAMES = ["industrialZone", "residentialZone", "centerZone"]

export const lambdaHandler = async (event: APIGatewayProxyEvent) => {
  for (let zone = 0; zone < POLLUTION_QUEUE_NAMES.length; zone++) {
    try {
      const commandDB = new PutItemCommand({
        TableName: "Pollution",
        Item: {
          zone: { S: POLLUTION_QUEUE_NAMES[zone] },
          pm10: { S: 0 + "µg/m3" },
          pm2_5: { S: 0 + "µg/m3" },
          timeStamp: { S: new_Date },
          dayTime: { S: fullDate },
          active: { BOOL: false },
        },
      })
      const responseDB = await ddbClient.send(commandDB)

      if (!responseDB) {
      } else {
        console.info("Database populated")
      }
    } catch (error) {
      console.error(error)
    }
  }
}
