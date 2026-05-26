# Customer Segmentation

**Author:** Example
**Date:** 2026-05-26
**Status:** approved

## Problem

The sushi team needs a customer segmentation model for order-frequency analysis.

## Users

| User | Job to be done |
|---|---|
| Growth analyst | Identify active, repeat, and dormant customers. |

## Acceptance Criteria

- AC1: When the customer segmentation model is queried, the system shall return one row per customer.
- AC2: Where a customer has no orders in the lookback window, the system shall classify the customer as dormant.
- AC3: When SQLMesh plan evidence is reviewed, the system shall show only the approved segmentation model and audit changes.

## Out of Scope

- New marketing activation exports.
