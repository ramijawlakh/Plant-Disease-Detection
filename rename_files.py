import os

def rename_images(directory, start_index=2568):
    images = sorted([f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
    
    for idx, filename in enumerate(images, start=start_index):
        ext = os.path.splitext(filename)[1]  # Get file extension
        new_name = f"rgb_{idx:04d}{ext}"
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        
    print("Renaming complete.")

def rename_txt(directory, start_index=2568):
    files = sorted([f for f in os.listdir(directory) if f.lower().endswith('.txt')])
    
    for idx, filename in enumerate(files, start=start_index):
        ext = os.path.splitext(filename)[1]  # Get file extension
        new_name = f"rgb_{idx:04d}{ext}"
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        
    print("Renaming complete.")

if __name__ == "__main__":
    dir_path = input("Enter the directory containing images: ")
    dir_path2 = input("Enter the directory containing txt files: ")
    rename_images(dir_path)
    rename_txt(dir_path2)
