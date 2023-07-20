import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb"

const REGION = process.env.REGION

//db client
const ddbClient = new DynamoDBClient({ region: REGION, endpoint: "http://localhost:4566" })

let zoneValue = ""
let result

//get timestamp
let new_Date = Date.now().toString()
let fullDate = new Date().toLocaleString()

export const lambdaHandler = async (event: any) => {
  const zone = event.zone

  try {
    const commandDB = new PutItemCommand({
      TableName: "Pollution",
      Item: {
        zone: { S: zone },
        pm10: { S: 0 + "µg/m3" },
        pm2_5: { S: 0 + "µg/m3" },
        Co2: { S: 0 + "g/km" },
        O2: { S: 0 + "µg/m3" },
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

const getValue = (max: number) => {
  return Math.floor(Math.random() * (max - 1)) + 1
}
