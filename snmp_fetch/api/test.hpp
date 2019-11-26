#include <list>
#include <optional>

struct A {
  int a;
};

inline bool operator==(const A& lhs, const A& rhs) {
  return lhs.a == rhs.a;
};

struct B {
  std::list<A> as;
  bool operator==(const B &other);
};

bool B::operator==(const B &other) {
  return this->as == other.as;
};
