import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb"
import { APIGatewayProxyEvent, APIGatewayProxyResult } from "aws-lambda"
import { ReceiveMessageCommand, DeleteMessageCommand, SQSClient } from "@aws-sdk/client-sqs"

const REGION = process.env.REGION

//db client
const ddbClient = new DynamoDBClient({ region: REGION, endpoint: "http://localhost:4566" })

//queues
const queueClient = new SQSClient({ region: REGION, endpoint: "http://localhost:4566" })

const POLLUTION_QUEUE_NAMES = ["industrialZone", "residentialZone", "centerZone"]

const SQS_QUEUE_URL = "http://localhost:4566/" + "/000000000000/"

export const lambdaHandler = async (event: APIGatewayProxyEvent) => {
  for (let queue = 0; queue < POLLUTION_QUEUE_NAMES.length; queue++) {
    let messageCount = 0
    let finalAveragePM10 = 0
    let finalAverage2_5 = 0

    try {
      const receiveMessageParams = {
        QueueUrl: SQS_QUEUE_URL + POLLUTION_QUEUE_NAMES[queue],
        MaxNumberOfMessages: 10, // Max number of messages to read
        WaitTimeSeconds: 5, // Max waiting time for messages (max value 20 secs)
      }

      const command = new ReceiveMessageCommand(receiveMessageParams)
      const response = await queueClient.send(command)
      const messages = response.Messages

      if (messages && messages.length > 0) {
        for (const message of messages) {
          messageCount++
          var body = JSON.parse(message.Body!)
          //console.info("SQS message received")
          finalAveragePM10 += parseInt(body.pm10.split(" ")[0])
          finalAverage2_5 += parseInt(body.pm2_5.split(" ")[0])
          /*console.log("Body message:", body)
          console.log("Average intermediate:", finalAveragePM10)*/

          await queueClient.send(
            new DeleteMessageCommand({
              QueueUrl: SQS_QUEUE_URL + POLLUTION_QUEUE_NAMES[queue],
              ReceiptHandle: message.ReceiptHandle,
            })
          )
          //console.info("Message eliminated")
        }
      }
      finalAveragePM10 = parseInt((finalAveragePM10 / messageCount).toFixed(2))
      finalAverage2_5 = parseInt((finalAverage2_5 / messageCount).toFixed(2))

      console.log("Average PM10 for", POLLUTION_QUEUE_NAMES[queue], ":", finalAveragePM10)
      console.log("Average PM2.5 for", POLLUTION_QUEUE_NAMES[queue], ":", finalAverage2_5)

      //Save into DynamoDB
      const commandDB = new PutItemCommand({
        TableName: "Pollution",
        Item: {
          zone: { S: POLLUTION_QUEUE_NAMES[queue] },
          pm10: { S: finalAveragePM10 + "µg/m3" },
          pm2_5: { S: finalAverage2_5 + "µg/m3" },
          timeStamp: { S: body.timeStamp },
          dayTime: { S: body.dayTime },
          active: { BOOL: true },
        },
      })
      const responseDB = await ddbClient.send(commandDB)

      if (!responseDB) {
      } else {
        console.info("Database populated")
      }
    } catch (error) {
      console.log("Error reading from queue", error)
    }
  }
}

//lambdaHandler()
