# Fair Assignment LINE Bot

A LINE bot that uses the Bogomolnaia-Moulin algorithm to make fair, envy-free assignments in group chats.

## Features

- Invite to any LINE group chat
- Fair assignment using proven algorithms
- Transparent probability distributions
- Randomized final assignments
- Easy-to-use chat interface

## How It Works

The bot implements the **Bogomolnaia-Moulin algorithm** from market design theory, which:

1. **Collects preferences** from all group members
2. **Simulates an "eating" process** where everyone consumes their top choices simultaneously
3. **Generates probability distributions** for fair assignments
4. **Provides concrete assignments** through randomized rounding

This ensures:
- ✅ **Strategy-proof**: No one can manipulate the outcome
- ✅ **Ordinally efficient**: No Pareto improvements possible
- ✅ **Envy-free**: No one prefers someone else's assignment

## Setup Instructions

### 1. Create a LINE Bot

1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Create a new provider and channel
3. Choose "Messaging API" as the channel type
4. Note down your **Channel Access Token** and **Channel Secret**

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

1. Copy `env_example.txt` to `.env`
2. Fill in your LINE bot credentials:
```bash
LINE_CHANNEL_ACCESS_TOKEN=your_actual_token_here
LINE_CHANNEL_SECRET=your_actual_secret_here
```

### 4. Deploy the Bot

#### Option A: Local Development
```bash
python app.py
```

#### Option B: Deploy to Cloud (Heroku, Railway, etc.)
1. Set up your deployment platform
2. Configure the webhook URL: `https://your-domain.com/callback`
3. Deploy the code

### 5. Configure Webhook

In your LINE Developers Console:
- Set webhook URL to: `https://your-domain.com/callback`
- Enable "Use webhook"
- Add your bot to group chats

## Usage

### Basic Commands

1. **Start Assignment Session**
   ```
   start assignment Research, Writing, Presentation
   ```

2. **Submit Rankings**
   ```
   3,1,2
   ```
   (This means: Presentation is 1st choice, Research is 2nd, Writing is 3rd)

3. **Check Status**
   ```
   status
   ```

4. **Run Algorithm**
   ```
   run algorithm
   ```

5. **Get Final Assignments**
   ```
   make assignments
   ```

### Example Session

```
User: start assignment Research, Writing, Presentation

Bot: 🎯 Starting fair assignment session!

Items to assign:
1. Research
2. Writing
3. Presentation

Please rank the items by replying with numbers separated by commas.
Example: '3,1,2' means item 3 is your top choice.

Type 'status' to see current progress.

User A: 3,1,2
User B: 1,3,2
User C: 2,1,3

User: run algorithm

Bot: 🎯 Bogomolnaia-Moulin Algorithm Results:

User A12345678...:
  Research: 33.3%
  Writing: 0.0%
  Presentation: 66.7%

User B87654321...:
  Research: 66.7%
  Writing: 0.0%
  Presentation: 33.3%

User C11111111...:
  Research: 0.0%
  Writing: 100.0%
  Presentation: 0.0%

Type 'make assignments' to get final assignments!

User: make assignments

Bot: 🎉 Final Assignments:

User A12345678... → Presentation
User B87654321... → Research
User C11111111... → Writing
```

## Algorithm Details

### Bogomolnaia-Moulin Algorithm

The algorithm simulates a "eating" process:

1. **Simultaneous Eating**: Everyone starts eating their top choice at rate 1
2. **Item Exhaustion**: When an item is fully consumed, people switch to their next choice
3. **Probability Calculation**: Each person's probability for an item equals the time they spent eating it
4. **Fairness Guarantees**: The resulting probabilities are strategy-proof and envy-free

### Mathematical Properties

- **Strategy-proof**: No participant can benefit from misreporting preferences
- **Ordinally efficient**: No Pareto improvements exist
- **Envy-free**: No participant prefers another's assignment
- **Equal treatment**: All participants are treated equally by the algorithm

## Use Cases

- **Task Assignment**: Assigning project tasks, chores, or responsibilities
- **Resource Allocation**: Distributing limited resources fairly
- **Role Assignment**: Assigning roles in events or activities
- **Study Group Formation**: Creating balanced study groups
- **Event Planning**: Assigning event responsibilities

## Technical Architecture

- **Backend**: Flask web server
- **LINE Integration**: LINE Messaging API
- **Algorithm**: Pure Python implementation of Bogomolnaia-Moulin
- **Data Storage**: In-memory (sessions reset on restart)
