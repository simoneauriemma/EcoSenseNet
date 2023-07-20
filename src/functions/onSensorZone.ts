import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb"

const REGION = process.env.REGION

//db client
const ddbClient = new DynamoDBClient({ region: REGION, endpoint: "http://localhost:4566" })

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
        pm10: { S: (result = getValue(35).toString() + "µg/m3") },
        pm2_5: { S: (result = getValue(25).toString() + "µg/m3") },
        Co2: { S: (result = getValue(95).toString() + "g/km") },
        O2: { S: (result = getValue(100).toString() + "µg/m3") },
        timeStamp: { S: new_Date },
        dayTime: { S: fullDate },
        active: { BOOL: true },
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
