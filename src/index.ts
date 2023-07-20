import * as dotenv from "dotenv"
import { SQSClient } from "@aws-sdk/client-sqs"
import { DynamoDBClient } from "@aws-sdk/client-dynamodb"

dotenv.config()

const ENDPOINT = process.env.ENDPOINT
const REGION = process.env.REGION

//db client
const ddbClient = new DynamoDBClient({ region: REGION, endpoint: ENDPOINT })

//queues
const queueClient = new SQSClient({ region: REGION, endpoint: ENDPOINT })

export { ddbClient, queueClient }
