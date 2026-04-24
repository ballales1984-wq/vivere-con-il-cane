## 🧪 Development & Testing

### Generating Realistic Test Data

The platform includes a management command to generate realistic dog profiles with historically accurate data:

```bash
# Generate 100 dogs with 30 days of health logs and medical history
python manage.py generate_real_dog_data --num-dogs 100 --days 30 --events 3
```

The generator creates:
- **Breed-appropriate profiles**: Realistic weights, dimensions, and activity levels
- **Historical health logs**: 30+ days of daily routine tracking (sleep, exercise, nutrition)
- **Medical event histories**: Correlated to breed predispositions and age
- **Diverse population**: Multiple breeds, ages (puppy to senior), and activity patterns

### Generated Data Statistics (100 Dogs)

- **Breeds**: 10 different breeds (10 dogs each)
- **Ages**: 1-14 years (realistic distribution)
- **Weight ranges**: Chihuahua (2.1 kg) to Pastore Tedesco (28.9 kg)
- **Health logs**: 3,000 daily entries
- **Medical events**: 270 events across breeds
- **Activity correlation**: Food intake (295-1,115g/day) correlates with activity level

### Data Validation

The generated data follows veterinary norms:
- ✅ **Weight-to-breed ratios**: Matched to AKC standards
- ✅ **Activity-to-caloric intake**: Proportional relationships
- ✅ **Breed health predispositions**: Bulldogs (respiratory), Labs (weight), etc.
- ✅ **Age-appropriate patterns**: Seniors sleep more, puppies play more

### Using Test Data

1. Login as `test_user_dog_data` (password: `test123456`)
2. Access any of the 103 dog profiles
3. Test AI diagnosis with different breeds and conditions
4. Run analytics on historical health patterns
5. Export veterinary dossiers for PDF/WhatsApp

### Reset Test Data

```bash
# Remove generated profiles
python manage.py shell -c "from dog_profile.models import DogProfile; DogProfile.objects.filter(owner__username='test_user_dog_data').delete()"

# Regenerate
python manage.py generate_real_dog_data --num-dogs 100 --days 30
```