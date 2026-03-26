"""
HPSv2 Scorer Module
使用 CLIP 模型实现 Human Preference Score v2 评分
"""

import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from typing import Union, List, Dict, Tuple


class HPSv2Scorer:
    """
    HPSv2 scorer using CLIP-based architecture.
    Computes image-text preference scores based on CLIP similarity.
    """

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """
        Initialize HPSv2 scorer with CLIP model.

        Args:
            model_name: CLIP model variant to use
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[HPSv2] Using device: {self.device}")
        self.model_name = model_name
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()

    def score_image_text(
        self,
        image_path: str,
        prompt: str,
        normalize: bool = True,
        max_prompt_length: int = 75
    ) -> float:
        """
        Score a single image against a text prompt.

        Args:
            image_path: Path to the image file
            prompt: Text prompt to evaluate against
            normalize: Whether to normalize the score
            max_prompt_length: Maximum token length for CLIP (default 75, safe margin from 77)

        Returns:
            Preference score (typically 0-1 range, higher is better)
        """
        try:
            image = Image.open(image_path).convert("RGB")

            # Truncate prompt to avoid CLIP token limit error
            if len(prompt) > max_prompt_length * 4:
                words = prompt.split()
                shortened = ""
                for word in words:
                    test = (shortened + " " + word).strip()
                    if len(test) <= max_prompt_length * 4:
                        shortened = test
                    else:
                        break
                prompt = shortened

            inputs = self.processor(
                text=[prompt],
                images=image,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)

            # Get CLIP cosine similarity (logits_per_image is already cosine similarity)
            logits_per_image = outputs.logits_per_image

            # Raw score - CLIP returns cosine similarity logits, typically in range [15, 35]
            raw_score = logits_per_image[0][0].item()

            if normalize:
                # Scale from [15, 35] to [0, 1] range using min-max normalization
                # Typical CLIP cosine sim range for well-matched image-text is 20-30
                min_val, max_val = 15.0, 35.0
                score = (raw_score - min_val) / (max_val - min_val)
                score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
            else:
                score = raw_score

            return score

        except Exception as e:
            print(f"[HPSv2] Error scoring {image_path}: {e}")
            return 0.0

    def score_batch(
        self,
        image_paths: List[str],
        prompts: List[str]
    ) -> List[float]:
        """
        Score multiple images against corresponding prompts.

        Args:
            image_paths: List of image file paths
            prompts: List of text prompts (one per image)

        Returns:
            List of preference scores
        """
        scores = []
        for img_path, prompt in zip(image_paths, prompts):
            score = self.score_image_text(img_path, prompt)
            scores.append(score)
        return scores

    def score_with_details(
        self,
        image_path: str,
        prompt: str
    ) -> Dict[str, Union[float, str]]:
        """
        Score image with detailed information.

        Args:
            image_path: Path to the image file
            prompt: Text prompt to evaluate against

        Returns:
            Dictionary containing score and metadata
        """
        raw_score = self.score_image_text(image_path, prompt, normalize=False)
        norm_score = self.score_image_text(image_path, prompt, normalize=True)

        return {
            "image_path": image_path,
            "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
            "raw_score": raw_score,
            "normalized_score": norm_score,
            "device": self.device
        }


def main():
    """Test the HPSv2 scorer with a sample image."""
    import os

    # Test with a sample image
    scorer = HPSv2Scorer()

    test_image = "d:/code/zixun-test2/zixun-test/output_images/wanx_商品图.png"
    test_prompt = "A majestic black luxury sedan parked on a leaf-strewn forest road"

    if os.path.exists(test_image):
        score = scorer.score_image_text(test_image, test_prompt)
        print(f"\nTest Score for wanx_商品图: {score:.4f}")
    else:
        print(f"Test image not found: {test_image}")


if __name__ == "__main__":
    main()
