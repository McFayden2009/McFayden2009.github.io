const fs = require('fs');
const path = require('path');

const dataFilePath = path.join(__dirname, '..', 'data.json');

exports.handler = async function(event, context) {
  const { method } = event;
  
  if (method === 'GET') {
    const data = fs.readFileSync(dataFilePath, 'utf-8');
    return {
      statusCode: 200,
      body: data
    };
  }

  if (method === 'POST' || method === 'DELETE') {
    let users = JSON.parse(fs.readFileSync(dataFilePath, 'utf-8'));
    const { userId, item } = JSON.parse(event.body);

    const userIndex = users.findIndex(user => user.id === userId);
    if (userIndex === -1) {
      return {
        statusCode: 404,
        body: JSON.stringify({ message: 'User not found' })
      };
    }

    if (method === 'POST') {
      users[userIndex].userData.push(item);
    } else if (method === 'DELETE') {
      users[userIndex].userData = users[userIndex].userData.filter(dataItem => dataItem !== item);
    }

    fs.writeFileSync(dataFilePath, JSON.stringify(users, null, 2));

    return {
      statusCode: 200,
      body: JSON.stringify(users[userIndex].userData)
    };
  }

  return {
    statusCode: 405,
    body: JSON.stringify({ message: 'Method not allowed' })
  };
}
