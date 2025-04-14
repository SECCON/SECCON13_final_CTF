#!/usr/bin/ruby
#!/usr/bin/ruby
# coding: utf-8
#
# mrubyバイトコード .mrb ファイルを読み込み、内容を表示する。
# v3.1 対応版
#
# (Usage)
#  mrbv31 [opt] .mrb file
#
# (Option)
#  -v   Verbose
#  -i   with indent
#  -d   Disassemble
#  -r   with a,b,c parameter values.
#

require "optparse"

#
# extend String
#
class String
  def to_int8( i = 0 )
    return self.getbyte(i) - ((self.getbyte(i) & 0x80) << 1)
  end

  def to_uint8( i = 0 )
    return self.getbyte(i)
  end

  def to_int16b( i = 0 )
    return (self.getbyte(i  ) << 8 |
            self.getbyte(i+1)) - ((self.getbyte(i) & 0x80) << 9)
  end

  def to_uint16b( i = 0 )
    return (self.getbyte(i  ) << 8 |
            self.getbyte(i+1))
  end

  def to_int16l( i = 0 )
    return (self.getbyte(i+1) << 8 |
            self.getbyte(i  )) - ((self.getbyte(i+1) & 0x80) << 9)
  end

  def to_uint16l( i = 0 )
    return (self.getbyte(i+1) << 8 |
            self.getbyte(i  ))
  end

  def to_int24b( i = 0 )
    return (self.getbyte(i  ) << 16 |
            self.getbyte(i+1) << 8  |
            self.getbyte(i+2)) - ((self.getbyte(i) & 0x80) << 17)
  end

  def to_uint24b( i = 0 )
    return (self.getbyte(i  ) << 16 |
            self.getbyte(i+1) << 8  |
            self.getbyte(i+2))
  end

  def to_int24l( i = 0 )
    return (self.getbyte(i+2) << 16 |
            self.getbyte(i+1) << 8  |
            self.getbyte(i  )) - ((self.getbyte(i+2) & 0x80) << 17)
  end

  def to_uint24l( i = 0 )
    return (self.getbyte(i+2) << 16 |
            self.getbyte(i+1) << 8  |
            self.getbyte(i  ))
  end

  def to_int32b( i = 0 )
    return (self.getbyte(i  ) << 24 |
            self.getbyte(i+1) << 16 |
            self.getbyte(i+2) << 8  |
            self.getbyte(i+3)) - ((self.getbyte(i) & 0x80) << 25)
  end

  def to_uint32b( i = 0 )
    return (self.getbyte(i  ) << 24 |
            self.getbyte(i+1) << 16 |
            self.getbyte(i+2) << 8  |
            self.getbyte(i+3))
  end

  def to_int32l( i = 0 )
    return (self.getbyte(i+3) << 24 |
            self.getbyte(i+2) << 16 |
            self.getbyte(i+1) << 8  |
            self.getbyte(i  )) - ((self.getbyte(i+3) & 0x80) << 25)
  end

  def to_uint32l( i = 0 )
    return (self.getbyte(i+3) << 24 |
            self.getbyte(i+2) << 16 |
            self.getbyte(i+1) << 8  |
            self.getbyte(i  ))
  end

  def to_fb( i = 0 )       # TODO
    return to_float64( self )
  end
  def to_fl( i = 0 )       # TODO
    buf = ""
    buf[0] = self[7]
    buf[1] = self[6]
    buf[2] = self[5]
    buf[3] = self[4]
    buf[4] = self[3]
    buf[5] = self[2]
    buf[6] = self[1]
    buf[7] = self[0]
    return to_float64( buf )
  end

end


#
# extend Integer
#
class Integer
  def bit( n, bw=1 )
    if n.class == Range
      if n.first > n.last
        msb = n.first
        lsb = n.last
      else
        lsb = n.first
        msb = n.last
      end
      bw = msb - lsb + 1
    else
      lsb = n - bw + 1
    end

    return (self >> lsb) & ((1 << bw) - 1)
  end

  def btest( n )
    return (self & (1 << n)) != 0
  end
end


def to_float64( s )
  # IEEE754 binary 64bit
  # b[63]     : sign bit
  # b[62..52] : exponent (11bits)
  # b[51..0]  : fraction (52bits)
  sign = s.getbyte(0) >> 7
  exp = ((s.getbyte(0) & 0x7f) << 4) | s.getbyte(1) >> 4
  frac = (0x10 | (s.getbyte(1) & 0x0f)) << 48 | s.getbyte(2) << 40 | s.getbyte(3) << 32 |
         s.getbyte(4) << 24 | s.getbyte(5) << 16 | s.getbyte(6) << 8 | s.getbyte(7)
#  p [sign,exp,frac.to_s(16), frac.to_f/2**52, exp-1023]

#  return 0.0 if exp == 0
#  exp = exp - 1023 #(bias)
#  frac = frac.to_f / 0x10_0000_0000_0000 #(= 2^52)
#  ret = (-1)**sign * frac * 2.0**exp
#   (thus)
#  ret = frac * 2.0 ** (exp - 1023 - 52)

  case exp
  when 0
    return 0.0
  when 0b111_1111_1111  # All 1
    #return (sign == 1) ? -1/0.0 : 1/0.0
    exp = 1023 - 52
    frac = 0x1f_ffff_ffff_ffff
  else
    exp -= 1075  # exp - 1023 - 52
  end

  x = 1.0
  exp.abs.times { x *= 2 }
  x = (exp >= 0) ? frac * x : frac / x
  return (sign == 1) ? -x : x
end

##
# hexdump
#
def hd( adrs, data, size )
  n = 0
  while n < size
    hbuf = sprintf("%04X  ", n + adrs )
    abuf = ""
    16.times {|i|
      hbuf << sprintf("%02x ", data.getbyte(n))
      hbuf << " " if i == 7
      abuf << (((" " <= data[n]) && (data[n] <= "~")) ? data[n] : ".")
      break if (n += 1) >= size
    }

    printf("%-55s %s\n", hbuf, abuf )
  end
end


##
# verbose function
#
def vp(*args)
  if $opt[:verbose]
    printf *args
  end
end


##
# RITEファイルヘッダの解析と表示
#
def read_binary_header( file )
  buf = file.read( 20 )
  if buf.length != 20
    puts "Error: can't read RITE FILE HEADER."
    exit 1
  end

  if buf[0..3] != "RITE"
    puts "RITE Identifier mismatch."
    exit 1
  end

  print "==== RITE FILE HEADER ====\n"
  print "Ident/Ver:", buf[0..7]

  size = buf.to_uint32b( 8 )
  printf "  Size:%d ($%X)", size, size
  print "  Compiler:", buf[16..19]
  print "\n\n"
end


##
# IREPセクションの解析
#
def read_section_irep( file, size )
  ver = file.read(4)
  print "ver:#{ver} ===\n"
  read_irep_record( file )
end

def read_irep_record( file, nest = 0, lvs = "" )
  ret = read_irep_record_1( file, nest, lvs )
  ret[:rlen].times {|i|
    read_irep_record( file, nest + 1, "#{lvs}-#{i}" )
  }
end

def read_irep_record_1( file, nest, lvs )
  # header
  rsize = file.read(4).to_uint32b()
  nlocals = file.read(2).to_uint16b()
  nregs = file.read(2).to_uint16b()
  rlen = file.read(2).to_uint16b()  # = reps
  clen = file.read(2).to_uint16b()
  ilen = file.read(4).to_uint32b()

  # op codes
  codes = file.read(ilen)

  # catch handlers
  catch_handlers = []
  clen.times {|i|
    catch_handlers << {
      ch_type: file.read(1).to_uint8(),
      ch_begin: file.read(4).to_uint32b(),
      ch_end: file.read(4).to_uint32b(),
      ch_target: file.read(4).to_uint32b()
    }
  }

  # POOL block
  pools = []
  plen = file.read(2).to_uint16b()
  plen.times {|i|
    tt = file.read(1).to_uint8()
    case tt
    when 1      # IREP_TT_INT32 32bit integer  irep.h irep_pool_type
      pools << { tt: tt, v: file.read(4).to_int32b() }

    when 3      # IREP_TT_INT64 64bit integer
      n1 = file.read(4).to_int32b()
      n2 = file.read(4).to_uint32b()
      pools << { tt: tt, v: (n1 << 32) | n2 }

    when 5      # IREP_TT_FLOAT float (double/float)
      pools << { tt: tt, v: file.read(8).to_fl() }

    when 0      # IREP_TT_STR   string
      n = file.read(2).to_uint16b()
      pools << { tt: tt, n: n, v: file.read(n), t: file.read(1) }

    else
      puts "Illegal tt (#{tt})"
    end
  }

  # SYMS block
  syms = []
  slen = file.read(2).to_uint16b()
  slen.times {|i|
    n = file.read(2).to_uint16b()
    syms << { n: n, v: file.read(n), t: file.read(1) }
  }

  #
  # display
  #
  print "> " * nest  if $opt[:indent_irep]
  print "[IREP#{lvs}] size:#{rsize} nlocals:#{nlocals} nregs:#{nregs} reps:#{rlen} clen:#{clen} ilen:#{ilen}\n"

  if $opt[:disassemble]
    disassemble( codes, catch_handlers, pools, syms )
  end

  if clen > 0
    print "  "*nest  if $opt[:indent_irep]
    print "[CATCH] clen:#{clen}\n"
    if $opt[:disassemble]
      catch_handlers.each_with_index {|ch,i|
        printf "  "*nest  if $opt[:indent_irep]
        printf "  %d: type=%d(%s)   begin=%03d end=%03d target=%03d\n",
               i, ch[:ch_type],
               ["rescue","ensure"][ch[:ch_type]],    # irep.h mrb_catch_type
               ch[:ch_begin], ch[:ch_end], ch[:ch_target]
      }
    end
  end

  print "  "*nest  if $opt[:indent_irep]
  print "[POOL] plen:#{plen}\n"
  pools.each_with_index {|pd, i|
    vp "  "*nest  if $opt[:indent_irep]
    case pd[:tt]
    when 1,3    # IREP_TT_INT*
      vp "  %d: type=%d val=%d\n", i, pd[:tt], pd[:v]

    when 5      # IREP_TT_FLOAT float (double/float)
      vp "  %d: type=%d val=%s\n", i, pd[:tt], pd[:v]

    when 0      # IREP_TT_STR   string
      vp "  %d: type=%d len=%d %s\n", i, pd[:tt], pd[:n], pd[:v].inspect
      raise "No zero terminate found." if pd[:t] != "\x00"
    end
  }

  print "  "*nest  if $opt[:indent_irep]
  print "[SYMS] slen:#{slen}\n"
  syms.each_with_index {|sym, i|
    vp "  "*nest  if $opt[:indent_irep]
    vp "  %d: len=%d %s\n", i, sym[:n], sym[:v].inspect
    puts "No zero terminate found." if sym[:t] != "\x00"
  }

  print "\n"
  return {rsize:rsize, nlocals:nlocals, nregs:nregs, rlen:rlen, clen:clen,
          ilen:ilen, plen:plen, slen:slen}
end


##
# DEBUG セクションの解析
#
def read_section_debug( file, size )
  puts "==="
  if $opt[:verbose]
    hd( 0, file.read( size-8 ), size-8 )
  else
    puts "(skip)"
  end
  puts
end


##
# LVAR セクションの解析
#
def read_section_lvar( file, size )
  puts "==="
  if $opt[:verbose]
    hd( 0, file.read( size-8 ), size-8 )
  else
    puts "(skip)"
  end
  puts
end


OP_EXT_PATTERN = {
  "B"  => %w(S),
  "BB" => %w(SB BS SS),
  "BBB"=> %w(SBB BSB SSB),
  "BS" => %w(SS SS SS),
  "BSS"=> %w(SSS),
}

##
# 逆アセンブル表示
#
def disassemble( codes, catch_handlers, pools, syms )
  #(note)
  # in $bytecode
  #  [code, "op_code", operands, semantics, sem_for_eval]
  idx = 0
  op_ext = nil
  while idx < codes.size
    addr = idx
    code = codes[idx].to_uint8()
    idx += 1
    op = $bytecode[ code ]
    if !op
      puts "Illegal bytecode #{code}"
      return
    end

    operand_pattern = op[2]
    if op_ext
      operand_pattern = OP_EXT_PATTERN[ operand_pattern ][ op_ext-1 ]
      if !operand_pattern
        puts "Illegal bytecode with op_ext."
        return
      end
      op_ext = nil
    end

    # check OP_EXT
    case op[1]
    when "OP_EXT1"; op_ext = 1
    when "OP_EXT2"; op_ext = 2
    when "OP_EXT3"; op_ext = 3
    end
    if op_ext
      printf(" %03d %02x %-13s %s\n", addr, code, op[1], eval('"' + op[4] + '"'))
      next
    end

    a = b = c = nil
    case operand_pattern
    when "Z"
      # nothing
    when "B"
      a = codes.to_uint8(idx)
      idx += 1
    when "BB"
      a = codes.to_uint8(idx)
      b = codes.to_uint8(idx+1)
      idx += 2
    when "BBB"
      a = codes.to_uint8(idx)
      b = codes.to_uint8(idx+1)
      c = codes.to_uint8(idx+2)
      idx += 3
    when "BS"
      a = codes.to_uint8(idx)
      b = codes.to_uint16b(idx+1)
      idx += 3
    when "BSS"
      a = codes.to_uint8(idx)
      b = codes.to_uint16b(idx+1)
      c = codes.to_uint16b(idx+3)
      idx += 5
    when "S"
      a = codes.to_uint16b(idx)
      idx += 2
    when "W"
      a = codes.to_uint24b(idx)
      idx += 3

    # with op_ext patterns
    when "SB"
      a = codes.to_uint16b(idx)
      b = codes.to_uint8(idx+2)
      idx += 3
    when "SS"
      a = codes.to_uint16b(idx)
      b = codes.to_uint16b(idx+2)
      idx += 4
    when "SBB"
      a = codes.to_uint16b(idx)
      b = codes.to_uint8(idx+2)
      c = codes.to_uint8(idx+3)
      idx += 4
    when "BSB"
      a = codes.to_uint8(idx)
      b = codes.to_uint16b(idx+1)
      c = codes.to_uint8(idx+3)
      idx += 4
    when "SSB"
      a = codes.to_uint16b(idx)
      b = codes.to_uint16b(idx+2)
      c = codes.to_uint8(idx+4)
      idx += 5
    when "SSS"
      a = codes.to_uint16b(idx)
      b = codes.to_uint16b(idx+2)
      c = codes.to_uint16b(idx+4)
      idx += 6
    else
      raise "Illegal operand pattern #{operand_pattern.inspect}"
    end

    case op[1]
    when "OP_JMP", "OP_JMPUW"
      a -= 0x10000  if a > 0x7fff
    when "OP_JMPIF", "OP_JMPNOT", "OP_JMPNIL", "OP_LOADI16"
      b -= 0x10000  if b > 0x7fff
    when /OP_S?SENDB?/
      n = (c & 0x0f)
      k = (c & 0xf0) >> 4
    end

    op1 = op[1].dup
    if $opt[:disp_reg]
      op1 << "("
      op1 << sprintf("%2d", a)  if a
      op1 << sprintf(",%2d", b)  if b
      op1 << sprintf(",%2d", c)  if c
      op1 << ")"
    end

    catch_handlers.each {|ch|
      next if ch[:ch_target] != addr
      printf("<%s>\n", ch[:ch_type] == 0 ? "rescue" : "ensure" )
    }

    printf(" %03d %02x %-18s %s\n", addr, code, op1, eval('"' + op[4] + '"'))
  end
end


##
# bytecodeテーブル生成
#
def create_bytecode_table()
  bytecode = []
  DATA.each_line.each_with_index {|s, i|
    if s !~ /^OPCODE\(([\w]+),\s*([ZBSW]+)\)\s*\/\*(.+)\*\/$/
      STDERR.puts "Illegal ops line #{i+1}: '#{s}'"
      exit 1
    end
    op = [i, "OP_#{$1}".freeze, $2, $3.strip.freeze]

    # semantics文字列を、evalしてoperand等の値が表示できるように書き換える
    # DATAで読むことができるsemanticsの書き方に依存しているので改変時注意
    sem = $3.strip
    if /S?SENDB?/ =~ $1                                         # OP_SEND...
      sem.gsub!(" (c=n|k<<4)", "")
      sem << ' [n=#{n},k=#{k}]'
    end

    sem.gsub!(/Syms\[([abc])\]/) {                              # Syms[a]
      "Syms[#{$1}=\#{#{$1}}]=:\#{syms[#{$1}][:v]}"
    }
    sem.gsub!(/Pool\[([abc])\]/) {                              # Pool[a]
      "Pool[#{$1}=\#{#{$1}}]=\#{pools[#{$1}][:v].inspect}"
    }
    sem.gsub!(/Irep\[([abc])\]/) {                              # Irep[a]
      "Irep[#{$1}=\#{#{$1}}]"
    }
    sem.gsub!(/mrb_int\((-)?(b)\)/) {                           # mrb_int(b)
      "mrb_int(#{$1}#{$2}=#{$1}\#{#{$2}})"
    }
    sem.gsub!(/R\[([abcn\+\-\*\d]+)\]/) {                       # R[a], R[a+n+1]
      "R[#{$1}=\#{#{$1}}]"
    }
    sem.gsub!(/\[c\]/) {
      "[c=\#{c}]"
    }
    sem.gsub!(/uv(set|get)\(b,c/) {                             # uvset/uvget
      "uv#{$1}(b=\#{b},c=\#{c}"
    }
    sem.gsub!(/pc\+=([ab])/) {                                  # pc+=a
      "pc += #{$1}=\#{#{$1}} = \#{sprintf('%03d', idx+#{$1})}"
    }
    sem.gsub!("R[a+n+2k+1]") {                                  # OP_SSENDB R[a+n+2k+1]
      "R[a+n+2k+1]=\#{a+n+2*k+1}]"
    }
    sem.gsub!("(b<<16)+c") {                                    # OP_LOADI32 (b<<16)+c
      '(b=#{b}<<16)+c=#{c} =#{(b<<16)+c - ((b & 0x8000) << 17)}'
    }
    sem.gsub!("unwind_and_jump_to(a)") {                        # OP_JMPUW
      'unwind_and_jump_to(a=#{a}) = #{sprintf("%03d", idx+a)}'
    }
    sem.gsub!("(16=m5:r1:m5:d1:lv4)") {                         # OP_ARGARY, OP_BLKPUSH
      '(m=#{b.bit(15,5)} r=#{b.bit(10)} m=#{b.bit(9,5)} d=#{b.bit(4)} lv=#{b.bit(3,4)})'
    }
    sem.gsub!("(23=m5:o5:r1:m5:k5:d1:b1)") {                    # OP_ENTER
      '(m=#{a.bit(22,5)} o=#{a.bit(17,5)} r=#{a.bit(12)} m=#{a.bit(11,5)} k=#{a.bit(6,5)} d=#{a.bit(1)} b=#{a.bit(0)})'
    }

    bytecode << (op << sem.freeze)
  }

  return bytecode.freeze
end


#
# main
#

# initialize bytecode table
$bytecode = create_bytecode_table()

# parse option
$opt = {:verbose=>false, :indent_irep=>false, :disassemble=>false, :disp_reg=>false}
begin
  opt = OptionParser.new
  opt.banner += " .rb/.mrb file"
  opt.on("-v", "verbose") {|v| $opt[:verbose] = v}
  opt.on("-i", "indent irep") {|v| $opt[:indent_irep] = v}
  opt.on("-d", "disassemble") {|v| $opt[:disassemble] = v}
  opt.on("-r", "with display registor variables") {|v| $opt[:disp_reg] = v}
  opt.parse!(ARGV)

  if !ARGV[0]
    puts opt.help
    exit 1
  end

rescue OptionParser::MissingArgument =>ex
  STDERR.puts ex.message
  return nil
end


# open the mrb file.
case File.extname(ARGV[0])
when ".mrb"
  file = open( ARGV[0] )
when ".rb"
  if !system("mrbc #{ARGV[0]}")
    exit 1
  end
  file = open( File.basename(ARGV[0], ".rb") + ".mrb" )
else
  puts "Argument error."
  exit 1
end

# parse
read_binary_header( file )
loop {
  pos = file.pos()
  id = file.read(4)
  size = file.read(4).to_uint32b()
  print "==== #{id.strip} SECTION size:#{size} ($#{size.to_s(16)}) "

  case id
  when "IREP"
    read_section_irep( file, size )
  when "DBG\x00"
    read_section_debug( file, size )
  when "LVAR"
    read_section_lvar( file, size )
  when "END\x00"
    puts "==="
    break
  else
    print "===\n(skip)\n\n"
  end

  file.seek( pos + size )
}


# mruby include/mruby/ops.hより
__END__
OPCODE(NOP,        Z)        /* no operation */
OPCODE(MOVE,       BB)       /* R[a] = R[b] */
OPCODE(LOADL,      BB)       /* R[a] = Pool[b] */
OPCODE(LOADI,      BB)       /* R[a] = mrb_int(b) */
OPCODE(LOADINEG,   BB)       /* R[a] = mrb_int(-b) */
OPCODE(LOADI__1,   B)        /* R[a] = mrb_int(-1) */
OPCODE(LOADI_0,    B)        /* R[a] = mrb_int(0) */
OPCODE(LOADI_1,    B)        /* R[a] = mrb_int(1) */
OPCODE(LOADI_2,    B)        /* R[a] = mrb_int(2) */
OPCODE(LOADI_3,    B)        /* R[a] = mrb_int(3) */
OPCODE(LOADI_4,    B)        /* R[a] = mrb_int(4) */
OPCODE(LOADI_5,    B)        /* R[a] = mrb_int(5) */
OPCODE(LOADI_6,    B)        /* R[a] = mrb_int(6) */
OPCODE(LOADI_7,    B)        /* R[a] = mrb_int(7) */
OPCODE(LOADI16,    BS)       /* R[a] = mrb_int(b) */
OPCODE(LOADI32,    BSS)      /* R[a] = mrb_int((b<<16)+c) */
OPCODE(LOADSYM,    BB)       /* R[a] = Syms[b] */
OPCODE(LOADNIL,    B)        /* R[a] = nil */
OPCODE(LOADSELF,   B)        /* R[a] = self */
OPCODE(LOADT,      B)        /* R[a] = true */
OPCODE(LOADF,      B)        /* R[a] = false */
OPCODE(GETGV,      BB)       /* R[a] = getglobal(Syms[b]) */
OPCODE(SETGV,      BB)       /* setglobal(Syms[b], R[a]) */
OPCODE(GETSV,      BB)       /* R[a] = Special[Syms[b]] */
OPCODE(SETSV,      BB)       /* Special[Syms[b]] = R[a] */
OPCODE(GETIV,      BB)       /* R[a] = ivget(Syms[b]) */
OPCODE(SETIV,      BB)       /* ivset(Syms[b],R[a]) */
OPCODE(GETCV,      BB)       /* R[a] = cvget(Syms[b]) */
OPCODE(SETCV,      BB)       /* cvset(Syms[b],R[a]) */
OPCODE(GETCONST,   BB)       /* R[a] = constget(Syms[b]) */
OPCODE(SETCONST,   BB)       /* constset(Syms[b],R[a]) */
OPCODE(GETMCNST,   BB)       /* R[a] = R[a]::Syms[b] */
OPCODE(SETMCNST,   BB)       /* R[a+1]::Syms[b] = R[a] */
OPCODE(GETUPVAR,   BBB)      /* R[a] = uvget(b,c) */
OPCODE(SETUPVAR,   BBB)      /* uvset(b,c,R[a]) */
OPCODE(GETIDX,     B)        /* R[a] = R[a][R[a+1]] */
OPCODE(SETIDX,     B)        /* R[a][R[a+1]] = R[a+2] */
OPCODE(JMP,        S)        /* pc+=a */
OPCODE(JMPIF,      BS)       /* if R[a] pc+=b */
OPCODE(JMPNOT,     BS)       /* if !R[a] pc+=b */
OPCODE(JMPNIL,     BS)       /* if R[a]==nil pc+=b */
OPCODE(JMPUW,      S)        /* unwind_and_jump_to(a) */
OPCODE(EXCEPT,     B)        /* R[a] = exc */
OPCODE(RESCUE,     BB)       /* R[b] = R[a].isa?(R[b]) */
OPCODE(RAISEIF,    B)        /* raise(R[a]) if R[a] */
OPCODE(SSEND,      BBB)      /* R[a] = self.send(Syms[b],R[a+1]..,R[a+n+1]:R[a+n+2]..) (c=n|k<<4) */
OPCODE(SSENDB,     BBB)      /* R[a] = self.send(Syms[b],R[a+1]..,R[a+n+1]:R[a+n+2]..,&R[a+n+2k+1]) */
OPCODE(SEND,       BBB)      /* R[a] = R[a].send(Syms[b],R[a+1]..,R[a+n+1]:R[a+n+2]..) (c=n|k<<4) */
OPCODE(SENDB,      BBB)      /* R[a] = R[a].send(Syms[b],R[a+1]..,R[a+n+1]:R[a+n+2]..,&R[a+n+2k+1]) */
OPCODE(CALL,       Z)        /* self.call(*, **, &) (But overlay the current call frame; tailcall) */
OPCODE(SUPER,      BB)       /* R[a] = super(R[a+1],... ,R[a+b+1]) */
OPCODE(ARGARY,     BS)       /* R[a] = argument array (16=m5:r1:m5:d1:lv4) */
OPCODE(ENTER,      W)        /* arg setup according to flags (23=m5:o5:r1:m5:k5:d1:b1) */
OPCODE(KEY_P,      BB)       /* R[a] = kdict.key?(Syms[b]) */
OPCODE(KEYEND,     Z)        /* raise unless kdict.empty? */
OPCODE(KARG,       BB)       /* R[a] = kdict[Syms[b]]; kdict.delete(Syms[b]) */
OPCODE(RETURN,     B)        /* return R[a] (normal) */
OPCODE(RETURN_BLK, B)        /* return R[a] (in-block return) */
OPCODE(BREAK,      B)        /* break R[a] */
OPCODE(BLKPUSH,    BS)       /* R[a] = block (16=m5:r1:m5:d1:lv4) */
OPCODE(ADD,        B)        /* R[a] = R[a]+R[a+1] */
OPCODE(ADDI,       BB)       /* R[a] = R[a]+mrb_int(b) */
OPCODE(SUB,        B)        /* R[a] = R[a]-R[a+1] */
OPCODE(SUBI,       BB)       /* R[a] = R[a]-mrb_int(b) */
OPCODE(MUL,        B)        /* R[a] = R[a]*R[a+1] */
OPCODE(DIV,        B)        /* R[a] = R[a]/R[a+1] */
OPCODE(EQ,         B)        /* R[a] = R[a]==R[a+1] */
OPCODE(LT,         B)        /* R[a] = R[a]<R[a+1] */
OPCODE(LE,         B)        /* R[a] = R[a]<=R[a+1] */
OPCODE(GT,         B)        /* R[a] = R[a]>R[a+1] */
OPCODE(GE,         B)        /* R[a] = R[a]>=R[a+1] */
OPCODE(ARRAY,      BB)       /* R[a] = ary_new(R[a],R[a+1]..R[a+b]) */
OPCODE(ARRAY2,     BBB)      /* R[a] = ary_new(R[b],R[b+1]..R[b+c]) */
OPCODE(ARYCAT,     B)        /* ary_cat(R[a],R[a+1]) */
OPCODE(ARYPUSH,    BB)       /* ary_push(R[a],R[a+1]..R[a+b]) */
OPCODE(ARYDUP,     B)        /* R[a] = ary_dup(R[a]) */
OPCODE(AREF,       BBB)      /* R[a] = R[b][c] */
OPCODE(ASET,       BBB)      /* R[b][c] = R[a] */
OPCODE(APOST,      BBB)      /* *R[a],R[a+1]..R[a+c] = R[a][b..] */
OPCODE(INTERN,     B)        /* R[a] = intern(R[a]) */
OPCODE(SYMBOL,     BB)       /* R[a] = intern(Pool[b]) */
OPCODE(STRING,     BB)       /* R[a] = str_dup(Pool[b]) */
OPCODE(STRCAT,     B)        /* str_cat(R[a],R[a+1]) */
OPCODE(HASH,       BB)       /* R[a] = hash_new(R[a],R[a+1]..R[a+b*2-1]) */
OPCODE(HASHADD,    BB)       /* hash_push(R[a],R[a+1]..R[a+b*2]) */
OPCODE(HASHCAT,    B)        /* R[a] = hash_cat(R[a],R[a+1]) */
OPCODE(LAMBDA,     BB)       /* R[a] = lambda(Irep[b],L_LAMBDA) */
OPCODE(BLOCK,      BB)       /* R[a] = lambda(Irep[b],L_BLOCK) */
OPCODE(METHOD,     BB)       /* R[a] = lambda(Irep[b],L_METHOD) */
OPCODE(RANGE_INC,  B)        /* R[a] = range_new(R[a],R[a+1],FALSE) */
OPCODE(RANGE_EXC,  B)        /* R[a] = range_new(R[a],R[a+1],TRUE) */
OPCODE(OCLASS,     B)        /* R[a] = ::Object */
OPCODE(CLASS,      BB)       /* R[a] = newclass(R[a],Syms[b],R[a+1]) */
OPCODE(MODULE,     BB)       /* R[a] = newmodule(R[a],Syms[b]) */
OPCODE(EXEC,       BB)       /* R[a] = blockexec(R[a],Irep[b]) */
OPCODE(DEF,        BB)       /* R[a].newmethod(Syms[b],R[a+1]); R[a] = Syms[b] */
OPCODE(ALIAS,      BB)       /* alias_method(target_class,Syms[a],Syms[b]) */
OPCODE(UNDEF,      B)        /* undef_method(target_class,Syms[a]) */
OPCODE(SCLASS,     B)        /* R[a] = R[a].singleton_class */
OPCODE(TCLASS,     B)        /* R[a] = target_class */
OPCODE(DEBUG,      BBB)      /* print a,b,c */
OPCODE(ERR,        B)        /* raise(LocalJumpError, Pool[a]) */
OPCODE(EXT1,       Z)        /* make 1st operand (a) 16bit */
OPCODE(EXT2,       Z)        /* make 2nd operand (b) 16bit */
OPCODE(EXT3,       Z)        /* make 1st and 2nd operands 16bit */
OPCODE(STOP,       Z)        /* stop VM */
