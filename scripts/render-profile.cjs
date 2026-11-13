// Execute the generated FlClash entry point with a profile supplied on stdin.
const fs = require("node:fs");
const vm = require("node:vm");
const profile = JSON.parse(fs.readFileSync(0, "utf8"));
const context = vm.createContext({ profile });
vm.runInContext(fs.readFileSync(process.argv[2], "utf8") + "\nresult = main(profile);", context, { timeout: 5000 });
process.stdout.write(JSON.stringify(context.result));
