// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.36.5
// 	protoc        v3.20.1
// source: nonce.proto

package proto

import (
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	emptypb "google.golang.org/protobuf/types/known/emptypb"
	reflect "reflect"
	sync "sync"
	unsafe "unsafe"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type NonceMessage struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Nonce         string                 `protobuf:"bytes,1,opt,name=nonce,proto3" json:"nonce,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *NonceMessage) Reset() {
	*x = NonceMessage{}
	mi := &file_nonce_proto_msgTypes[0]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *NonceMessage) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*NonceMessage) ProtoMessage() {}

func (x *NonceMessage) ProtoReflect() protoreflect.Message {
	mi := &file_nonce_proto_msgTypes[0]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use NonceMessage.ProtoReflect.Descriptor instead.
func (*NonceMessage) Descriptor() ([]byte, []int) {
	return file_nonce_proto_rawDescGZIP(), []int{0}
}

func (x *NonceMessage) GetNonce() string {
	if x != nil {
		return x.Nonce
	}
	return ""
}

type ValidMessage struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Valid         bool                   `protobuf:"varint,1,opt,name=valid,proto3" json:"valid,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *ValidMessage) Reset() {
	*x = ValidMessage{}
	mi := &file_nonce_proto_msgTypes[1]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *ValidMessage) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*ValidMessage) ProtoMessage() {}

func (x *ValidMessage) ProtoReflect() protoreflect.Message {
	mi := &file_nonce_proto_msgTypes[1]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use ValidMessage.ProtoReflect.Descriptor instead.
func (*ValidMessage) Descriptor() ([]byte, []int) {
	return file_nonce_proto_rawDescGZIP(), []int{1}
}

func (x *ValidMessage) GetValid() bool {
	if x != nil {
		return x.Valid
	}
	return false
}

var File_nonce_proto protoreflect.FileDescriptor

var file_nonce_proto_rawDesc = string([]byte{
	0x0a, 0x0b, 0x6e, 0x6f, 0x6e, 0x63, 0x65, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x12, 0x05, 0x6e,
	0x6f, 0x6e, 0x63, 0x65, 0x1a, 0x1b, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x2f, 0x70, 0x72, 0x6f,
	0x74, 0x6f, 0x62, 0x75, 0x66, 0x2f, 0x65, 0x6d, 0x70, 0x74, 0x79, 0x2e, 0x70, 0x72, 0x6f, 0x74,
	0x6f, 0x22, 0x24, 0x0a, 0x0c, 0x4e, 0x6f, 0x6e, 0x63, 0x65, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67,
	0x65, 0x12, 0x14, 0x0a, 0x05, 0x6e, 0x6f, 0x6e, 0x63, 0x65, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09,
	0x52, 0x05, 0x6e, 0x6f, 0x6e, 0x63, 0x65, 0x22, 0x24, 0x0a, 0x0c, 0x56, 0x61, 0x6c, 0x69, 0x64,
	0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x12, 0x14, 0x0a, 0x05, 0x76, 0x61, 0x6c, 0x69, 0x64,
	0x18, 0x01, 0x20, 0x01, 0x28, 0x08, 0x52, 0x05, 0x76, 0x61, 0x6c, 0x69, 0x64, 0x32, 0x7c, 0x0a,
	0x0c, 0x4e, 0x6f, 0x6e, 0x63, 0x65, 0x53, 0x65, 0x72, 0x76, 0x69, 0x63, 0x65, 0x12, 0x36, 0x0a,
	0x05, 0x4e, 0x6f, 0x6e, 0x63, 0x65, 0x12, 0x16, 0x2e, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x2e,
	0x70, 0x72, 0x6f, 0x74, 0x6f, 0x62, 0x75, 0x66, 0x2e, 0x45, 0x6d, 0x70, 0x74, 0x79, 0x1a, 0x13,
	0x2e, 0x6e, 0x6f, 0x6e, 0x63, 0x65, 0x2e, 0x4e, 0x6f, 0x6e, 0x63, 0x65, 0x4d, 0x65, 0x73, 0x73,
	0x61, 0x67, 0x65, 0x22, 0x00, 0x12, 0x34, 0x0a, 0x06, 0x52, 0x65, 0x64, 0x65, 0x65, 0x6d, 0x12,
	0x13, 0x2e, 0x6e, 0x6f, 0x6e, 0x63, 0x65, 0x2e, 0x4e, 0x6f, 0x6e, 0x63, 0x65, 0x4d, 0x65, 0x73,
	0x73, 0x61, 0x67, 0x65, 0x1a, 0x13, 0x2e, 0x6e, 0x6f, 0x6e, 0x63, 0x65, 0x2e, 0x56, 0x61, 0x6c,
	0x69, 0x64, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x22, 0x00, 0x42, 0x2c, 0x5a, 0x2a, 0x67,
	0x69, 0x74, 0x68, 0x75, 0x62, 0x2e, 0x63, 0x6f, 0x6d, 0x2f, 0x6c, 0x65, 0x74, 0x73, 0x65, 0x6e,
	0x63, 0x72, 0x79, 0x70, 0x74, 0x2f, 0x62, 0x6f, 0x75, 0x6c, 0x64, 0x65, 0x72, 0x2f, 0x6e, 0x6f,
	0x6e, 0x63, 0x65, 0x2f, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x62, 0x06, 0x70, 0x72, 0x6f, 0x74, 0x6f,
	0x33,
})

var (
	file_nonce_proto_rawDescOnce sync.Once
	file_nonce_proto_rawDescData []byte
)

func file_nonce_proto_rawDescGZIP() []byte {
	file_nonce_proto_rawDescOnce.Do(func() {
		file_nonce_proto_rawDescData = protoimpl.X.CompressGZIP(unsafe.Slice(unsafe.StringData(file_nonce_proto_rawDesc), len(file_nonce_proto_rawDesc)))
	})
	return file_nonce_proto_rawDescData
}

var file_nonce_proto_msgTypes = make([]protoimpl.MessageInfo, 2)
var file_nonce_proto_goTypes = []any{
	(*NonceMessage)(nil),  // 0: nonce.NonceMessage
	(*ValidMessage)(nil),  // 1: nonce.ValidMessage
	(*emptypb.Empty)(nil), // 2: google.protobuf.Empty
}
var file_nonce_proto_depIdxs = []int32{
	2, // 0: nonce.NonceService.Nonce:input_type -> google.protobuf.Empty
	0, // 1: nonce.NonceService.Redeem:input_type -> nonce.NonceMessage
	0, // 2: nonce.NonceService.Nonce:output_type -> nonce.NonceMessage
	1, // 3: nonce.NonceService.Redeem:output_type -> nonce.ValidMessage
	2, // [2:4] is the sub-list for method output_type
	0, // [0:2] is the sub-list for method input_type
	0, // [0:0] is the sub-list for extension type_name
	0, // [0:0] is the sub-list for extension extendee
	0, // [0:0] is the sub-list for field type_name
}

func init() { file_nonce_proto_init() }
func file_nonce_proto_init() {
	if File_nonce_proto != nil {
		return
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: unsafe.Slice(unsafe.StringData(file_nonce_proto_rawDesc), len(file_nonce_proto_rawDesc)),
			NumEnums:      0,
			NumMessages:   2,
			NumExtensions: 0,
			NumServices:   1,
		},
		GoTypes:           file_nonce_proto_goTypes,
		DependencyIndexes: file_nonce_proto_depIdxs,
		MessageInfos:      file_nonce_proto_msgTypes,
	}.Build()
	File_nonce_proto = out.File
	file_nonce_proto_goTypes = nil
	file_nonce_proto_depIdxs = nil
}
