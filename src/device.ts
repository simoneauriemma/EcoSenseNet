import { SendMessageCommand } from "@aws-sdk/client-sqs"

import { queueClient } from "./index"

const POLLUTION_QUEUE_NAMES = ["industrialZone", "residentialZone", "centerZone"]

const SQS_QUEUE_URL = process.env.ENDPOINT + "/000000000000/"

//get timestamp
let new_Date = Date.now().toString()
let fullDate = new Date().toLocaleString()

const getValue = (max: number) => {
  return Math.floor(Math.random() * max)
}

const getRandomIntInclusive = (min: number, max: number) => {
  min = Math.ceil(min)
  max = Math.floor(max)
  return Math.floor(Math.random() * (max - min + 1) + min)
}

const uploadToQueues = async (sqsQueueUrl = SQS_QUEUE_URL) => {
  for (let queue = 0; queue < POLLUTION_QUEUE_NAMES.length; queue++) {
    let random = getRandomIntInclusive(2, 5)

    for (let count = 0; count < random; count++) {
      const command = new SendMessageCommand({
        QueueUrl: SQS_QUEUE_URL + POLLUTION_QUEUE_NAMES[queue],
        DelaySeconds: 1,
        MessageBody: `{ "zone":"${POLLUTION_QUEUE_NAMES[queue].toString()}","pm10":"${getValue(
          35
        ).toString()} µg/m3","pm2_5":"${getValue(25).toString()} µg/m3","Co2":"${getValue(
          95
        ).toString()} g/km","O2":"${getValue(
          100
        ).toString()} µg/m3","timeStamp":"${new_Date}","dayTime":"${fullDate}"}`,
      })
      const response = await queueClient.send(command)

      if (!response) {
        console.error("Error sending to queue", POLLUTION_QUEUE_NAMES[queue])
      }
      console.info("Message sent")
    }
  }
}

uploadToQueues()
