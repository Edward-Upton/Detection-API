
# LEGO Brick Detection Server/API

## What is This?

LEGO have been manufacturing bricks and parts since 1947 and since then they have accumlilated over 8,000 different overall designs and over 60,000 different variants. This has come with issues with the identification of the bricks. LEGO introduced their own ID system with each design having a "DESIGN ID" and each variant having a "ELEMENT ID". Third parties have used these IDs to create online databases, such as BrickSet, Rebrickable and BrickOwl. But each of these sites use difficult naming systems and it is difficult for a typical person to identify a part and find the corresponding IDs. This is where my solution comes in.

## Brick Identification

The whole system uses deep learning to create models to identify bricks.

### Creating Training Images

Straight away it was clear that manually taking and labelling up images was going to be too lengthy even with a small variety of parts to test with. Instead, I am using an open-source ray tracing program called POV-RAY. 