# Excel to MongoDB Migration Scripts

This directory contains comprehensive scripts to migrate data from Excel files to MongoDB for the Smart Kitchen Queue Management System.

## 📋 Available Scripts

### 1. **excel_to_mongodb.py** (Async Version)
- **Description**: Full-featured async migration script using motor
- **Best for**: Advanced users, production environments
- **Requirements**: `pandas`, `openpyxl`, `motor`, `asyncio`

### 2. **excel_to_mongodb_sync.py** (Sync Version) ⭐ **Recommended**
- **Description**: Simpler synchronous version using pymongo
- **Best for**: Most users, easier to use and debug
- **Requirements**: `pandas`, `openpyxl`, `pymongo`

### 3. **migrate_excel_to_mongodb.bat** (Windows)
- **Description**: Windows batch script with interactive prompts
- **Best for**: Windows users who prefer GUI-like experience
- **Requirements**: Python + packages (auto-installs if missing)

### 4. **migrate_excel_to_mongodb.sh** (Linux/Mac)
- **Description**: Shell script with interactive prompts
- **Best for**: Linux/Mac users who prefer command-line
- **Requirements**: Python + packages (auto-installs if missing)

## 🚀 Quick Start

### Option 1: Simple Command Line (Recommended)

```bash
# Install requirements
pip install pandas openpyxl pymongo

# Run migration
python excel_to_mongodb_sync.py
```

### Option 2: Interactive Scripts

**Windows:**
```cmd
migrate_excel_to_mongodb.bat
```

**Linux/Mac:**
```bash
chmod +x migrate_excel_to_mongodb.sh
./migrate_excel_to_mongodb.sh
```

## 📊 Excel File Requirements

Your Excel file must contain these sheets:

### 1. **items** sheet
Required columns:
- `item_id` - Unique identifier (string/number)
- `item_name` - Name of the menu item
- `kitchen_id` - Which kitchen handles this item
- `prep_time_minutes` - Preparation time in minutes

Optional columns:
- `category` - Food category (appetizer, main, etc.)
- `difficulty_level` - easy, medium, hard
- `description` - Item description
- `price` - Item price
- `available` - true/false availability
- `calories` - Nutritional information
- `allergens` - Comma-separated allergens

### 2. **kitchens** sheet
Required columns:
- `kitchen_id` - Unique identifier
- `kitchen_name` - Name of the kitchen
- `capacity` - Maximum concurrent items

Optional columns:
- `specialization` - Kitchen specialty
- `status` - active, inactive, maintenance
- `current_load` - Current workload
- `staff_count` - Number of staff
- `equipment` - Comma-separated equipment list

## 🔧 Command Line Options

### Basic Usage
```bash
python excel_to_mongodb_sync.py [options]
```

### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--excel-file PATH` | Path to Excel file | `data/kitchen_config.xlsx` |
| `--mongodb-url URL` | MongoDB connection URL | `mongodb://127.0.0.1:27017` |
| `--database NAME` | Database name | `smart_kitchen` |
| `--clear-existing` | Clear existing data before import | False |
| `--dry-run` | Preview what would be imported | False |
| `--verbose` | Enable detailed logging | False |

### Examples

```bash
# Basic migration
python excel_to_mongodb_sync.py

# Custom Excel file
python excel_to_mongodb_sync.py --excel-file my_data.xlsx

# Clear existing data and import
python excel_to_mongodb_sync.py --clear-existing

# Preview what would be imported
python excel_to_mongodb_sync.py --dry-run

# Custom MongoDB connection
python excel_to_mongodb_sync.py --mongodb-url "mongodb://user:pass@localhost:27017" --database my_kitchen

# Verbose logging
python excel_to_mongodb_sync.py --verbose
```

## 📈 What Gets Migrated

### Menu Items Collection (`menu_items`)
```json
{
  "item_id": "1",
  "item_name": "Classic Spring Rolls",
  "name": "Classic Spring Rolls",
  "kitchen_id": "KITCHEN_001",
  "prep_time_minutes": 8,
  "prep_time": 8,
  "category": "appetizer",
  "difficulty": "easy",
  "available": true,
  "price": 8.99,
  "sync_source": "excel_migration",
  "synced_at": "2024-01-01T12:00:00Z"
}
```

### Kitchens Collection (`kitchens`)
```json
{
  "kitchen_id": "KITCHEN_001",
  "kitchen_name": "Appetizer Station",
  "name": "Appetizer Station",
  "capacity": 3,
  "specialization": "appetizers",
  "status": "active",
  "current_load": 0,
  "staff_count": 2,
  "sync_source": "excel_migration",
  "synced_at": "2024-01-01T12:00:00Z"
}
```

## 🔍 Validation & Error Handling

### Pre-Migration Checks
- ✅ Excel file exists and is readable
- ✅ Required sheets are present
- ✅ MongoDB connection is working
- ✅ Required columns exist

### During Migration
- ✅ Data type validation
- ✅ Duplicate handling (upsert behavior)
- ✅ Error logging with details
- ✅ Transaction safety

### Post-Migration
- ✅ Data count verification
- ✅ Index creation for performance
- ✅ Connection cleanup

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Excel file not found**
```
❌ Excel file not found: data/kitchen_config.xlsx
```
**Solution**: Ensure the Excel file exists at the specified path

#### 2. **Missing required sheets**
```
❌ Missing required sheets: ['items']
```
**Solution**: Add the missing sheets to your Excel file

#### 3. **MongoDB connection failed**
```
❌ Failed to connect to MongoDB: [Errno 111] Connection refused
```
**Solution**: 
- Start MongoDB service
- Check connection URL
- Verify MongoDB is running on specified port

#### 4. **Missing Python packages**
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution**: Install required packages
```bash
pip install pandas openpyxl pymongo
```

#### 5. **Permission errors**
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: 
- Run with appropriate permissions
- Check file/directory permissions
- Close Excel file if it's open

### Debug Mode
Enable verbose logging to see detailed information:
```bash
python excel_to_mongodb_sync.py --verbose
```

## 📊 Performance Tips

### For Large Excel Files
- Use `--verbose` to monitor progress
- Consider splitting large files into smaller chunks
- Ensure sufficient RAM for pandas operations

### For MongoDB
- Ensure MongoDB has sufficient disk space
- Use appropriate connection pooling
- Monitor MongoDB logs during migration

## 🔄 Migration Workflow

```mermaid
graph TD
    A[Start Migration] --> B[Validate Excel File]
    B --> C[Connect to MongoDB]
    C --> D[Clear Existing Data?]
    D -->|Yes| E[Clear Collections]
    D -->|No| F[Load Excel Data]
    E --> F
    F --> G[Validate Data]
    G --> H[Import to MongoDB]
    H --> I[Create Indexes]
    I --> J[Verify Results]
    J --> K[Complete]
```

## 🎯 Best Practices

### Before Migration
1. **Backup existing MongoDB data**
2. **Validate Excel file structure**
3. **Test with `--dry-run` first**
4. **Ensure MongoDB is running**

### During Migration
1. **Monitor logs for errors**
2. **Don't interrupt the process**
3. **Ensure stable network connection**

### After Migration
1. **Verify data counts**
2. **Test application functionality**
3. **Monitor MongoDB performance**
4. **Keep Excel file as backup**

## 🆘 Support

If you encounter issues:

1. **Check logs** with `--verbose` flag
2. **Verify Excel file structure**
3. **Test MongoDB connection separately**
4. **Review error messages carefully**
5. **Try `--dry-run` to preview changes**

## 📝 Example Excel File Structure

Create an Excel file with these sheets:

**Sheet: items**
| item_id | item_name | kitchen_id | prep_time_minutes | category | price |
|---------|-----------|------------|-------------------|----------|-------|
| 1 | Classic Spring Rolls | KITCHEN_001 | 8 | appetizer | 8.99 |
| 2 | Buffalo Wings | KITCHEN_001 | 12 | appetizer | 12.99 |

**Sheet: kitchens**
| kitchen_id | kitchen_name | capacity | specialization | status |
|------------|--------------|----------|----------------|--------|
| KITCHEN_001 | Appetizer Station | 3 | appetizers | active |
| KITCHEN_002 | Main Kitchen | 5 | mains | active |

---

## 🎉 Success!

After successful migration, your MongoDB database will be ready for the Smart Kitchen Queue Management System with all menu items and kitchen configurations properly imported and indexed for optimal performance.
