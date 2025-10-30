import json
import os
import random
import requests
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

def upload_to_freeimage(image_path, api_key):
    """
    Upload an image to Freeimage.host
    
    Args:
        image_path: Full path to the image file
        api_key: Your Freeimage.host API key
    
    Returns:
        dict: Response data including image URL
    """
    url = "https://freeimage.host/api/1/upload"
    
    try:
        # Open the image file
        with open(image_path, 'rb') as image_file:
            # Prepare the request
            files = {
                'source': image_file
            }
            
            data = {
                'key': api_key,
                'action': 'upload',
                'format': 'json',
                'type': 'file',
                'nsfw': '0'
            }
            
            # Make the POST request
            response = requests.post(url, files=files, data=data)
            
            # Check if request was successful
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status_code') == 200:
                    return {
                        'success': True,
                        'url': result['image']['url'],
                        'display_url': result['image']['display_url'],
                        'delete_url': result['image'].get('delete_url'),
                        'thumb_url': result['image'].get('thumb', {}).get('url'),
                        'image_id': result['image'].get('id'),
                        'raw_response': result
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', {}).get('message', 'Unknown error'),
                        'error_code': result.get('error', {}).get('code'),
                        'raw_response': result
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
    
    except FileNotFoundError:
        return {
            'success': False,
            'error': f'File not found: {image_path}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def verify_image_access(url, timeout=10):
    """
    Verify that an uploaded image is accessible
    
    Args:
        url: Image URL to check
        timeout: Request timeout in seconds
    
    Returns:
        dict: Access check results
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return {
            'accessible': response.status_code == 200,
            'status_code': response.status_code,
            'error': None if response.status_code == 200 else f'HTTP {response.status_code}'
        }
    except Exception as e:
        return {
            'accessible': False,
            'status_code': None,
            'error': str(e)
        }

def delete_image(delete_url):
    """
    Delete an image using the delete URL (if available)
    
    Args:
        delete_url: Delete URL returned from upload
        
    Returns:
        bool: Whether deletion was successful
    """
    if not delete_url:
        return False
    
    try:
        response = requests.get(delete_url, timeout=10)
        return response.status_code == 200
    except:
        return False

def save_dataset(dataset, dataset_json):
    """
    Save the dataset to JSON file
    """
    with open(dataset_json, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

def upload_car_dataset(dataset_json='car_dataset.json', api_key=None, delay_seconds=5, 
                       rate_limit_pause=3600, max_retries=3):
    """
    Upload all images from car_dataset.json to Freeimage.host
    Detects rate limiting and pauses when needed
    
    Args:
        dataset_json: Path to the JSON file (will be updated in place)
        api_key: Your Freeimage.host API key
        delay_seconds: Delay between uploads
        rate_limit_pause: How long to pause when rate limit detected (in seconds, default 1 hour)
        max_retries: Maximum retry attempts for failed uploads
    """
    
    if not api_key:
        print("ERROR: API key is required!")
        print("Get your API key from: https://freeimage.host/page/api")
        return
    
    # Load the dataset
    try:
        with open(dataset_json, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {dataset_json} not found!")
        return
    
    print(f"Loaded {len(dataset)} total images")
    
    # Count how many already have URLs
    already_uploaded = sum(1 for entry in dataset if entry.get('hosted_url') and entry.get('upload_status') == 'success')
    to_upload = len(dataset) - already_uploaded
    
    print(f"Already uploaded: {already_uploaded}")
    print(f"To upload: {to_upload}")
    print(f"Starting upload process...\n")
    
    # Track statistics
    successful = 0
    failed = 0
    skipped = 0
    uploads_this_session = 0
    consecutive_403s = 0
    
    # Process each image
    idx: int = 0
    for entry in dataset:
        idx += 1
        if random.randint(1, 100) <= 80:
            print(f"[{idx}/{len(dataset)}] Skipping (random skip): {Path(entry['file_path']).name}")
            continue

        # Skip if already successfully uploaded
        if entry.get('hosted_url') and entry.get('upload_status') == 'success':
            skipped += 1
            print(f"[{idx}/{len(dataset)}] Skipping (already uploaded): {Path(entry['file_path']).name}")
            continue
        
        file_path = entry['file_path']
        retry_count = entry.get('retry_count', 0)
        
        # Skip if too many retries
        if retry_count >= max_retries:
            print(f"[{idx}/{len(dataset)}] Skipping (max retries exceeded): {Path(file_path).name}")
            continue
        
        print(f"[{idx}/{len(dataset)}] Uploading: {Path(file_path).name}" + 
              (f" (retry {retry_count + 1})" if retry_count > 0 else ""))
        
        # Upload the image
        result = upload_to_freeimage(file_path, api_key)
        
        if result['success']:
            uploads_this_session += 1
            
            # CRITICAL: Verify immediately
            print(f"  → Verifying accessibility...")
            time.sleep(2 + random.randint(0, 5))  # Brief delay before verification
            access_check = verify_image_access(result['url'])
            
            if access_check['accessible']:
                # SUCCESS!
                entry['hosted_url'] = result['url']
                entry['display_url'] = result['display_url']
                entry['thumb_url'] = result.get('thumb_url')
                entry['delete_url'] = result.get('delete_url')
                entry['image_id'] = result.get('image_id')
                entry['upload_status'] = 'success'
                entry['access_verified'] = True
                entry['last_upload_time'] = datetime.now().isoformat()
                if 'retry_count' in entry:
                    del entry['retry_count']
                
                successful += 1
                consecutive_403s = 0
                print(f"  ✓ Success: {result['url']}")
                
            else:
                # UPLOAD RETURNED 200 BUT IMAGE IS INACCESSIBLE (RATE LIMITED!)
                print(f"  ✗ Upload returned 200 but image is INACCESSIBLE: {access_check['error']}")
                # print(f"  → This indicates rate limiting. Image is permanently broken.")
                
                # Try to delete the broken image
                if result.get('delete_url'):
                    print(f"  → Attempting to delete broken image...")
                    delete_image(result['delete_url'])
                
                
                # consecutive_403s += 1
                
                # # If we've hit multiple consecutive 403s, we've hit the rate limit
                # if consecutive_403s >= 2:
                #     print(f"\n{'='*60}")
                #     print(f"⚠️  RATE LIMIT DETECTED!")
                #     print(f"{'='*60}")
                #     print(f"Uploaded {uploads_this_session} images this session")
                #     print(f"Pausing for {rate_limit_pause // 60} minutes...")
                #     print(f"Resume time: {datetime.now()}")
                #     print(f"{'='*60}\n")
                    
                #     # Save current progress
                #     # save_dataset(dataset, dataset_json)
                    
                #     # # Long pause
                #     # time.sleep(rate_limit_pause)
                    
                #     # Reset counters
                #     uploads_this_session = 0
                #     consecutive_403s = 0
                    
                #     print(f"\nResuming uploads...")
                # else:
                #     # Mark for retry
                #     entry['upload_status'] = 'rate_limited'
                #     entry['upload_error'] = f'Rate limit detected - upload succeeded but image inaccessible'
                #     entry['retry_count'] = retry_count + 1
                #     entry['last_upload_time'] = datetime.now().isoformat()
                    
                failed += 1
        else:
            # Upload itself failed
            entry['upload_status'] = 'failed'
            entry['upload_error'] = result['error']
            entry['retry_count'] = retry_count + 1
            entry['last_upload_time'] = datetime.now().isoformat()
            failed += 1
            print(f"  ✗ Upload failed: {result['error']}")
        
        # Save after each attempt
        save_dataset(dataset, dataset_json)
        
        # Delay between uploads
        time.sleep(delay_seconds)
    
    # Print summary
    print("\n" + "="*60)
    print("UPLOAD COMPLETE!")
    print("="*60)
    print(f"Total images: {len(dataset)}")
    print(f"Skipped (already uploaded): {skipped}")
    print(f"Newly uploaded: {successful}")
    print(f"Failed/Rate limited: {failed}")
    print(f"Dataset saved to: {dataset_json}")
    
    # Show images that need retry
    need_retry = [e for e in dataset if e.get('upload_status') in ['rate_limited', 'failed'] 
                  and e.get('retry_count', 0) < max_retries]
    if need_retry:
        print(f"\n{len(need_retry)} images need retry. Run script again to retry.")
    
    return dataset

if __name__ == "__main__":
    load_dotenv()
    root_folder = os.path.dirname(os.path.abspath(__file__)) 

    result = upload_car_dataset(
        dataset_json=os.path.join(root_folder, "../car_dataset.json"),
        api_key=os.getenv("API_KEY"),
        delay_seconds=5,         # 5 seconds between uploads
        rate_limit_pause=3600,   # Wait 1 hour when rate limit detected
        max_retries=3            # Try each image up to 3 times
    )