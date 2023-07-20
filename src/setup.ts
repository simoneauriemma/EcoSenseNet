import { runDB } from "./settings/createDB"
import { createQueues } from "./settings/createQueues"

const tableSetup = runDB()
  .then(() => console.info("Table created"))
  .catch((err) => console.error(err))

const queueSetup = createQueues()
  .then(() => console.info("Queues created"))
  .catch((err) => console.error(err))
