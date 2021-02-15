from car_racing import *

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers



if __name__ == "__main__":
    

    render = False
    

    num_inputs = 16
    num_actions = 9
    num_hidden = 128

    action_choices = [[0,1,0],[0,0,1],[0,0,0],[1,1,0],[1,0,1],[1,0,0],[-1,1,0],[-1,0,1],[-1,0,0]]

    inputs = layers.Input(shape=(num_inputs,))
    common = layers.Dense(num_hidden, activation="relu")(inputs)
    action = layers.Dense(num_actions, activation="softmax")(common)
    critic = layers.Dense(1)(common)

    #model = keras.Model(inputs=inputs, outputs=[action, critic]) 
    model = keras.models.load_model("./model") #charger modèle existant
    gamma = 0.99  # Discount factor for past rewards
    eps = np.finfo(np.float32).eps.item()  # Smallest number such that 1.0 + eps != 1.0
    env = CarRacing()

    if render:
        env.render()

    optimizer = keras.optimizers.Adam(learning_rate=0.01)
    huber_loss = keras.losses.Huber()
    action_probs_history = []
    critic_value_history = []
    rewards_history = []
    running_reward = 0
    episode_count = 0
    max_episode = 1000
    while episode_count < max_episode:
        state = env.reset()
        env.setAngleZero()
        episode_reward = 0
        steps = 0
        
        restart = False
        if episode_count == 00:  #commencer à render après x itérations
            env.render()
            render = True

        with tf.GradientTape() as tape:
            while True:

                state = tf.convert_to_tensor(state)
                state = tf.expand_dims(state, 0)

                # Predict action probabilities and estimated future rewards
                # from environment state
                action_probs, critic_value = model(state)
                critic_value_history.append(critic_value[0, 0])

                # Sample action from action probability distribution
                action = np.random.choice(num_actions, p=np.squeeze(action_probs))
                action_probs_history.append(tf.math.log(action_probs[0, action]))
                a = action_choices[action]

                state,reward, done = env.step(a)
                rewards_history.append(reward)
                episode_reward += reward
                """
                if steps % 200 == 0 or done:
                    print("\naction " + str(["{:+0.2f}".format(x) for x in a]))
                    print("step {} total_reward {:+0.2f}".format(steps, episode_reward))
                """
                steps += 1
                if render:
                    isopen = env.render()
                if done or restart or episode_reward < -200: #arrête si le reward total est trop bas (voiture presque immobile)
                    episode_reward-=300
                    rewards_history.append(reward)
                    break

            # Calculate expected value from rewards
            # - At each timestep what was the total reward received after that timestep
            # - Rewards in the past are discounted by multiplying them with gamma
            # - These are the labels for our critic
            returns = []
            discounted_sum = 0
            for r in rewards_history[::-1]:
                discounted_sum = r + gamma * discounted_sum
                returns.insert(0, discounted_sum)

            # Normalize
            returns = np.array(returns)
            returns = (returns - np.mean(returns)) / (np.std(returns) + eps)
            returns = returns.tolist()

            # Calculating loss values to update our network
            history = zip(action_probs_history, critic_value_history, returns)
            actor_losses = []
            critic_losses = []
            for log_prob, value, ret in history:
                # At this point in history, the critic estimated that we would get a
                # total reward = `value` in the future. We took an action with log probability
                # of `log_prob` and ended up recieving a total reward = `ret`.
                # The actor must be updated so that it predicts an action that leads to
                # high rewards (compared to critic's estimate) with high probability.
                diff = ret - value
                actor_losses.append(-log_prob * diff)  # actor loss

                # The critic must be updated so that it predicts a better estimate of
                # the future rewards.
                critic_losses.append(
                    huber_loss(tf.expand_dims(value, 0), tf.expand_dims(ret, 0))
                )

            # Backpropagation
            loss_value = sum(actor_losses) + sum(critic_losses)
            grads = tape.gradient(loss_value, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables))

            # Clear the loss and reward history
            action_probs_history.clear()
            critic_value_history.clear()
            rewards_history.clear()
        # Log details
        episode_count += 1
        print("{} tiles visited on run".format(env.tile_visited_count))
        print("episode {}".format(episode_count))
        
        if episode_count % 10 == 0:
            template = "running reward: {} at episode {}"
            print(template.format(env.times_succeeded, episode_count))
        if episode_count %100 == 0:
            model.save("./model")
        if env.times_succeeded > 5:  # Condition to consider the task solved
            print("Solved at episode {}!".format(episode_count))
            break
    model.save("./model")
    env.close()