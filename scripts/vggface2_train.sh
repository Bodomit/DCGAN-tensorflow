#!/usr/bin/env bash
python main.py --dataset vggface2 --data_dir /datasets --input_fname_pattern="train/*/*.jpg" --out_dir /results --input_height=64 --output_height=64 --train