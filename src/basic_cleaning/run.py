#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Drop data outside NYC
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    # Export as a CSV
    df.to_csv(args.output_artifact, index=False)
    
    # Upload the cleaned sample data
    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)
    run.finish()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This steps cleans the data")


    parser.add_argument(
        "--min_price", 
        type=int,
        help="Minimum price of the Airbnb listings to analyze",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=int,
        help="Maximum price of the Airbnb listings to analyze",
        required=True
    )
    
    parser.add_argument(
        '--input_artifact',
        type=str,
        required=True,
        help='Name of the input artifact'
    )

    parser.add_argument(
        '--output_artifact',
        type=str,
        required=True,
        help='Name for the output artifact'
    )

    parser.add_argument(
        '--output_type',
        type=str,
        required=True,
        help='Type of the output artifact'
    )

    parser.add_argument(
        '--output_description',
        type=str,
        required=True,
        help='Description of the output artifact'
    )

    args = parser.parse_args()

    go(args)
