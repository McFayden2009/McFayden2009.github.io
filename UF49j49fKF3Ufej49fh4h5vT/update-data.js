const fs = require('fs');
const path = './data.json';

// Function to read the JSON file
const readData = () => {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
};

// Function to write to the JSON file
const writeData = (data) => {
  fs.writeFileSync(path, JSON.stringify(data, null, 2));
};

// Update this function with your logic to update the JSON file
const updateData = () => {
  const data = readData();

  // Example: Adding a new item to user 1's data
  const userIndex = data.findIndex(user => user.id === 1);
  if (userIndex !== -1) {
    data[userIndex].userData.push("New Item");
  }

  writeData(data);
};

// Run the update function
updateData();
