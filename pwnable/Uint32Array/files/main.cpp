#include <iostream>
#include <cstdint>

class Uint32Array {
public:
  Uint32Array() : _size(0), _buffer(nullptr) {}
  Uint32Array(size_t size) : _size(size), _buffer(new uint32_t[size]()) {}
  ~Uint32Array() { delete[] _buffer; }

  void clear() {
    for (ssize_t i = 0; i < _size; i++)
      _buffer[i] = 0;
  }

  uint32_t& at(size_t index) {
    if (index >= _size)
      throw std::out_of_range("out-of-bounds access");
    return _buffer[index];
  }

private:
  size_t _size;
  uint32_t *_buffer;
};

void AskArray(Uint32Array& arr) {
  size_t size = 0;
  do {
    std::cout << "size = ";
    std::cin >> size;
  } while (size > 100);

  arr = Uint32Array(size);
  arr.clear();
}

void AskIndex(size_t& index) {
  std::cout << "index = ";
  std::cin >> index;
}

void AskValue(uint32_t& value) {
  std::cout << "value = ";
  std::cin >> value;
}

int main() {
  Uint32Array arr;
  uint32_t value;
  size_t index;
  std::cin.rdbuf()->pubsetbuf(nullptr, 0);
  std::cout.rdbuf()->pubsetbuf(nullptr, 0);

  AskArray(arr);

  std::cout << "1. set" << std::endl
            << "2. get" << std::endl;
  while (std::cin.good()) {
    int choice;
    std::cout << "> ";
    std::cin >> choice;

    if (choice == 1) {
      AskIndex(index);
      AskValue(value);
      try {
        arr.at(index) = value;
      } catch(const std::out_of_range& e) {
        std::cout << "[ERR] " << e.what() << std::endl
                  << "[ERR] Would you like to enter recovery mode? [y=1/N=0]: ";
        std::cin >> choice;
        if (choice == 1) {
          std::cout << "[ERR] Entering recovery mode: Try again." << std::endl;
          AskIndex(index);
          AskValue(value);
          arr.at(index) = value;
        }
      }

    } else if (choice == 2) {
      AskIndex(index);
      std::cout << "arr[" << index << "] = " << arr.at(index) << std::endl;

    } else {
      std::cout << "Bye!" << std::endl;
      break;
    }
  }

  return 0;
}
