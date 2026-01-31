# Transformer Architecture

## Introduction

The Transformer architecture is a deep learning model introduced in the paper "Attention Is All You Need" (Vaswani et al., 2017). It is designed for handling sequential data, such as natural language, but unlike RNNs, it relies entirely on attention mechanisms rather than recurrence.

## How It Differs from RNN

- **No Recurrence:** Transformers process all input tokens in parallel, while RNNs process data sequentially.

- **Long-Range Dependencies:** Transformers use self-attention to directly connect all positions in a sequence, making it easier to capture long-range relationships. RNNs struggle with long-term dependencies due to vanishing gradients.

- **Parallelization:** Transformers allow for much greater parallelization during training, leading to faster and more efficient computation compared to the inherently sequential RNNs.

## What It Solves Compared to RNN

- **Overcomes Vanishing/Exploding Gradients:** By removing recurrence, transformers avoid the vanishing/exploding gradient problems common in RNNs.

- **Efficient Long-Context Learning:** Self-attention enables the model to learn relationships between distant tokens more effectively.

- **Scalability:** Transformers scale better to large datasets and models, enabling breakthroughs in NLP and beyond.

## Core Architecture Overview

- **Input Embedding:** Converts input tokens into dense vectors.

- **Positional Encoding:** Adds information about token positions, since transformers lack inherent sequence order.

- **Encoder Stack:** A series of identical layers, each with multi-head self-attention and feed-forward networks.

- **Decoder Stack:** Similar to the encoder, but includes mechanisms for attending to encoder outputs and previous decoder outputs.

- **Output Layer:** Produces the final predictions (e.g., translated text, generated sequence).

### Transformer Architecture Block Diagram

```plaintext
+----------------+   +---------------------+   +-------------------+   +-------------------+   +----------------+
| Input Embedding|-->| Positional Encoding |-->| Encoder Stack     |-->| Decoder Stack     |-->| Output Layer   |
+----------------+   +---------------------+   +-------------------+   +-------------------+   +----------------+
```

This diagram shows the high-level flow of data through the main components of the Transformer architecture.

## Why Transformers Are Better Than RNNs for Understanding Context

Transformers outperform RNNs in understanding the full context of a sentence due to their use of self-attention mechanisms. Here’s how and why:

### RNNs: Limited Contextual Understanding

- **Sequential Processing:** RNNs process input tokens one at a time, passing information from one step to the next. Each token's representation is influenced mainly by its immediate neighbors and the hidden state carried forward.

- **Long-Range Dependency Problem:** As the sequence grows, information from earlier tokens can get diluted or lost due to vanishing gradients, making it hard for RNNs to capture relationships between distant words.

- **Local Context:** In practice, RNNs are best at understanding local context—how a word relates to its nearby words—rather than the entire sentence at once.

### Transformers: Global Context with Self-Attention

- **Self-Attention Mechanism:** Transformers use self-attention, which allows every token in the input to directly attend to every other token, regardless of their position in the sequence.

- **Parallel Processing:** All tokens are processed simultaneously, and each token’s representation is updated based on a weighted combination of all other tokens in the sentence.

- **Global Relationships:** This means the model can easily learn relationships between any two words, no matter how far apart they are. For example, in the sentence "The cat, which was black, sat on the mat," the word "cat" can directly influence the representation of "sat" even though they are separated by several words.

- **No Information Loss:** Since all tokens interact in each layer, there is no risk of information being lost over long distances, as happens in RNNs.

### Summary Table

| Aspect              | RNN                                             | Transformer                               |
| ------------------- | ----------------------------------------------- | ----------------------------------------- |
| Contextual Range    | Local (neighboring tokens)                      | Global (all tokens in the sequence)       |
| Processing          | Sequential (one token at a time)                | Parallel (all tokens at once)             |
| Long-Range Learning | Difficult (vanishing gradients)                 | Easy (self-attention connects all tokens) |
| Information Flow    | Step-by-step, can lose info over long sequences | Direct, no loss over distance             |

Transformers’ ability to model all pairwise relationships in a sequence at every layer is the key reason they have become the foundation for modern NLP models, replacing RNNs in most applications.

## Attention Mechanism and Self-Attention

### What is Attention?

The attention mechanism is a technique that allows neural networks to focus on specific parts of the input sequence when making predictions. Instead of treating all input tokens equally, attention assigns different weights to different tokens, enabling the model to prioritize the most relevant information for each output.

### Self-Attention

Self-attention (or intra-attention) is a special case where the model computes attention scores between all pairs of tokens in the same sequence. This allows each token to gather contextual information from every other token, regardless of their position.

#### How Self-Attention Works

1. **Input Embeddings:** Each token in the sequence is converted into a vector (embedding).

2. **Query, Key, Value Vectors:** For each token, three vectors are computed: Query (Q), Key (K), and Value (V), using learned weight matrices.

3. **Attention Scores:** The attention score between two tokens is computed as the dot product of their Query and Key vectors, followed by a softmax to normalize the scores.

4. **Weighted Sum:** Each token’s output is a weighted sum of all Value vectors, where the weights are the attention scores.

5. **Multi-Head Attention:** Multiple self-attention operations (heads) are run in parallel, allowing the model to capture different types of relationships.

### Self-Attention Architecture (Block Diagram)

```plaintext
+---------+     +---------+     +---------+     +---------+     +---------+
| Input   | --> | Linear  | --> | Q, K, V | --> | Attention| --> | Output  |
| Tokens  |     | Layers  |     | Vectors |     | Weights  |     | Vectors |
+---------+     +---------+     +---------+     +---------+     +---------+
```

## Tokenizer

A tokenizer is a preprocessing tool that splits raw text into smaller units called tokens (words, subwords, or characters). These tokens are then mapped to numerical IDs for input into the model. Tokenization is essential for converting human language into a format that neural networks can process.

## Encoder

The encoder is the part of the transformer that processes the input sequence. It consists of multiple layers, each containing multi-head self-attention and feed-forward networks. The encoder transforms the input tokens into rich contextual representations that capture the meaning and relationships between tokens.

## Decoder

The decoder is responsible for generating the output sequence (e.g., translated text). It also consists of multiple layers, each with self-attention, encoder-decoder attention (to focus on relevant parts of the input), and feed-forward networks. The decoder produces the final output tokens one by one, using both the encoder’s output and previously generated tokens as context.

## How Encoder and Decoder Understand a Sentence

### Encoder: Understanding the Input

1. **Tokenization:** The input sentence is split into tokens and converted into embeddings.

2. **Positional Encoding:** Positional information is added to each token embedding to retain word order.

3. **Self-Attention Layers:** Each token attends to all other tokens in the sentence, gathering contextual information and building a rich representation for every token.

4. **Feed-Forward Layers:** The output from self-attention is further processed to enhance feature extraction.

5. **Stacking Layers:** Multiple encoder layers repeat the self-attention and feed-forward process, deepening the model’s understanding of the sentence.

6. **Final Output:** The encoder produces a set of contextualized vectors, each representing a token with full awareness of the entire sentence.

### Decoder: Generating and Understanding Output

1. **Input Preparation:** The decoder receives the encoder’s output and, during generation, the previously generated tokens.

2. **Masked Self-Attention:** The decoder uses masked self-attention to ensure each output token only attends to earlier tokens, preserving the left-to-right generation order.

3. **Encoder-Decoder Attention:** Each decoder token attends to all encoder outputs, allowing the decoder to focus on relevant parts of the input sentence for each output step.

4. **Feed-Forward Layers:** The combined information is processed through feed-forward layers for further transformation.

5. **Stacking Layers:** Multiple decoder layers repeat the attention and feed-forward process, refining the output at each step.

6. **Final Output:** The decoder generates the next token in the sequence, using both the encoder’s understanding of the input and the context of previously generated tokens.

### How Attention Ensures Understanding

- **Self-Attention:** Allows every token to consider the entire sentence, capturing relationships and context.

- **Encoder-Decoder Attention:** Enables the decoder to selectively focus on the most relevant parts of the input for each output token, ensuring accurate and context-aware generation.

- **Layer Stacking:** Deep stacking of attention layers allows for complex, hierarchical understanding of language and meaning.
