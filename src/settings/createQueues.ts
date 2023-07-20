import { CreateQueueCommand } from "@aws-sdk/client-sqs"

import { queueClient } from "../index"

const POLLUTION_QUEUE_NAMES = ["industrialZone", "residentialZone", "centerZone"]

export const createQueues = async (sqsQueueName = POLLUTION_QUEUE_NAMES) => {
  for (let queue = 0; queue < POLLUTION_QUEUE_NAMES.length; queue++) {
    const command = new CreateQueueCommand({
      QueueName: POLLUTION_QUEUE_NAMES[queue],
      Attributes: {
        DelaySeconds: "60",
        MessageRetentionPeriod: "86400",
      },
    })

    const response = await queueClient.send(command)

    if (!response) {
      console.error("Error. Queue", POLLUTION_QUEUE_NAMES[queue], "not created")
    }

    console.log("Queue", POLLUTION_QUEUE_NAMES[queue], "created")
  }
}
