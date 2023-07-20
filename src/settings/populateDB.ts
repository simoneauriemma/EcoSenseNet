import { PutItemCommand } from "@aws-sdk/client-dynamodb"

import { ddbClient } from "../index"

//zones array for creating entries in db
const POLLUTION_QUEUE_NAMES = ["industrialZone", "residentialZone", "centerZone"]
//variables for store the random result
let result
//get timestamp
let new_Date = Date.now().toString()
let fullDate = new Date().toLocaleString()

export const populateDB = async () => {
  for (let zone = 0; zone < POLLUTION_QUEUE_NAMES.length; zone++) {
    const command = new PutItemCommand({
      TableName: "Pollution",
      Item: {
        zone: { S: POLLUTION_QUEUE_NAMES[zone] },
        pm10: { S: (result = getValue(35).toString() + "µg/m3") },
        pm2_5: { S: (result = getValue(25).toString() + "µg/m3") },
        Co2: { S: (result = getValue(95).toString() + "g/km") },
        O2: { S: (result = getValue(100).toString() + "µg/m3") },
        timeStamp: { S: new_Date },
        dayTime: { S: fullDate },
        active: { BOOL: true },
      },
    })
    const response = await ddbClient.send(command)

    if (!response) {
      console.error("Error populating DB\n")
    }
    console.info("Database populated")
  }
}

const getValue = (max: number) => {
  return Math.floor(Math.random() * (max - 1)) + 1
}

populateDB()
